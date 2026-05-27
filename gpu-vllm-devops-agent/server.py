import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Optional

import requests
from google.cloud import aiplatform, secretmanager, storage
from google.cloud import logging as cloud_logging
from mcp.server.fastmcp import FastMCP

# Setup logging to stderr ONLY to avoid interfering with MCP stdio communication
logging.basicConfig(
    stream=sys.stderr, level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("vllm-devops-agent")
logger.info("Initializing DevOps Agent MCP Server...")

# Initialize FastMCP server
mcp = FastMCP("Self-Hosted vLLM DevOps Agent")

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "aisprint-491218")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4")
BUCKET_NAME = f"{PROJECT_ID}-bucket"
# The URL of the self-hosted vLLM service on Cloud Run
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-4-E4B-it")
HF_SECRET_ID = "hf-token"


async def get_secret(secret_id: str = HF_SECRET_ID) -> Optional[str]:
    """Retrieves a secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    try:
        response = await asyncio.to_thread(client.access_secret_version, request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception:
        return None


@mcp.tool()
async def save_hf_token(token: str) -> str:
    """Securely saves a Hugging Face API token to GCP Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    secret_parent = f"projects/{PROJECT_ID}/secrets/{HF_SECRET_ID}"

    try:
        # Check if the secret already exists
        await asyncio.to_thread(client.get_secret, request={"name": secret_parent})
    except Exception:
        # If not, create it
        await asyncio.to_thread(
            client.create_secret,
            request={
                "parent": f"projects/{PROJECT_ID}",
                "secret_id": HF_SECRET_ID,
                "secret": {"replication": {"automatic": {}}},
            },
        )

    # Add the new version
    response = await asyncio.to_thread(
        client.add_secret_version,
        request={"parent": secret_parent, "payload": {"data": token.encode("UTF-8")}},
    )
    return f"✅ Token saved. Version: {response.name}"


def discover_vllm_url(service_name: str = "vllm-gemma-4-e4b-it") -> Optional[str]:
    """Attempts to automatically discover the Cloud Run service URL."""
    if VLLM_BASE_URL:
        logger.info(f"Using provided VLLM_BASE_URL: {VLLM_BASE_URL}")
        return VLLM_BASE_URL

    logger.info(f"Attempting to discover vLLM URL for service: {service_name}")
    try:
        cmd = [
            "gcloud",
            "run",
            "services",
            "describe",
            service_name,
            f"--project={PROJECT_ID}",
            "--region",
            LOCATION,
            "--format",
            "value(status.url)",
        ]
        # Added timeout and improved error handling
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if process.returncode == 0:
            url = process.stdout.strip()
            if url:
                logger.info(f"📡 Automatically discovered vLLM at: {url}")
                return url
            else:
                logger.warning("⚠️ gcloud returned empty URL for service.")
        else:
            logger.warning(
                f"⚠️ gcloud failed to discover Cloud Run URL (code {process.returncode}): {process.stderr.strip()}"
            )
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ Discovery timed out after 15 seconds.")
    except Exception as e:
        logger.warning(f"⚠️ Error during vLLM discovery: {str(e)}")

    logger.error("❌ Failed to discover Cloud Run URL and localhost fallback is disabled.")
    return None


# Resolve base URL at runtime
_ACTIVE_VLLM_URL = None


def get_vllm_url() -> str:
    """Returns the cached vLLM URL or discovers it if needed."""
    global _ACTIVE_VLLM_URL
    # If not set, try discovering it
    if not _ACTIVE_VLLM_URL:
        _ACTIVE_VLLM_URL = discover_vllm_url()

    if not _ACTIVE_VLLM_URL:
        raise Exception(
            "Could not determine vLLM Cloud Run URL. Ensure you are authenticated with gcloud and the service exists."
        )

    return _ACTIVE_VLLM_URL


def get_auth_token() -> str:
    """Gets a Google Cloud Identity Token for authenticating to Cloud Run."""
    try:
        # Use a timeout for the token generation too
        return (
            subprocess.check_output(
                ["gcloud", "auth", "print-identity-token"],
                stderr=subprocess.DEVNULL,
                timeout=10,
            )
            .decode("utf-8")
            .strip()
        )
    except Exception as e:
        logger.warning(f"⚠️ Could not obtain identity token: {str(e)}")
        return ""


# Initialize Vertex AI SDK
aiplatform.init(project=PROJECT_ID, location=LOCATION)


@mcp.resource("config://vllm-deployment-template")
def get_deployment_template() -> str:
    """Returns a base template for Cloud Run GPU deployment."""
    return f"""
# Cloud Run vLLM Deployment Template
# Required: Second Generation execution environment
# Required: NVIDIA L4 GPU
# Required: GCS FUSE mount

service: vllm-gemma-4-e4b-it
image: vllm/vllm-openai:latest
resources:
  limits:
    nvidia.com/gpu: 1
    cpu: 4
    memory: 16Gi
annotations:
  run.googleapis.com/execution-environment: gen2
  run.googleapis.com/gpu-zonal-redundancy-disabled: "true"
  run.googleapis.com/cpu-throttling: "false"  # Mandatory for GPU
  run.googleapis.com/startup-cpu-boost: "true"
  run.googleapis.com/maxScale: "1"
container:
  concurrency: 4
  timeout: 3600s
startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 180
  periodSeconds: 60
  failureThreshold: 10
  timeoutSeconds: 60
# For gcloud deployment, use:
# gcloud run deploy vllm-gemma-4-e4b-it --no-cpu-throttling --allow-unauthenticated --concurrency=4 \\
#   --timeout=3600 --startup-probe=timeoutSeconds=60,periodSeconds=60,failureThreshold=10,initialDelaySeconds=180,httpGet.port=8000,httpGet.path=/health \\
#   --max-instances=1 --args=--model=/mnt/models/gemma-4-E4B-it,--max-model-len=4096,--trust-remote-code,--gpu-memory-utilization=0.9,--host=0.0.0.0
volumes:
  - name: model-volume
    cloudStorage:
      bucket: {BUCKET_NAME}
      readonly: true
"""


@mcp.tool()
def get_vllm_endpoint(service_name: str = "vllm-gemma-4-e4b-it") -> Optional[str]:
    """
    Returns the current active vLLM endpoint URL.

    Args:
        service_name: The Cloud Run service name to describe (defaults to 'vllm-gemma-4-e4b-it').
    """
    # If it's the default service, use our cached discovery logic
    if service_name == "vllm-gemma-4-e4b-it":
        return get_vllm_url()
    return discover_vllm_url(service_name)


@mcp.tool()
def list_vertex_models() -> str:
    """
    Uses the Vertex AI SDK (part of ADK ecosystem) to list models in the project registry.
    """
    try:
        models = aiplatform.Model.list()
        if not models:
            return "No models found in Vertex AI Model Registry."

        model_list = [f"- {m.display_name} (ID: {m.name})" for m in models]
        return "### Vertex AI Model Registry\n" + "\n".join(model_list)
    except Exception as e:
        return f"Error listing models from Vertex AI: {str(e)}"


@mcp.tool()
def list_bucket_models(bucket_name: str = BUCKET_NAME) -> str:
    """
    Lists the contents of the GCS bucket to check for uploaded model files.

    Args:
        bucket_name: The GCS bucket name to check. Defaults to BUCKET_NAME.
    """
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(bucket_name)
        # List up to 100 blobs
        blobs = list(bucket.list_blobs(max_results=100))

        if not blobs:
            return f"The bucket '{bucket_name}' is empty."

        # Display up to 50 for brevity
        file_list = [f"- {b.name} ({b.size / 1024 / 1024:.2f} MB)" for b in blobs[:50]]
        summary = f"### Contents of GCS Bucket: {bucket_name}\n"
        summary += "\n".join(file_list)

        if len(blobs) > 50:
            summary += f"\n\n(Showing 50 of {len(blobs)} items)"

        return summary
    except Exception as e:
        return f"Error listing objects in bucket '{bucket_name}': {str(e)}"


@mcp.tool()
async def analyze_cloud_logging(filter_query: str, limit: int = 5) -> str:
    """
    Fetches and summarizes error logs from Google Cloud Logging using a self-hosted vLLM endpoint on Cloud Run.

    Args:
        filter_query: Filter for Cloud Logging (e.g., 'severity=ERROR').
        limit: Number of recent logs to fetch.
    """
    try:
        logging_client = cloud_logging.Client(project=PROJECT_ID)
        entries = list(
            logging_client.list_entries(filter_=filter_query, order_by=cloud_logging.DESCENDING, page_size=limit)
        )

        if not entries:
            return "No matching logs found."

        log_texts = [
            f"Timestamp: {e.timestamp} | Severity: {e.severity} | Message: {str(e.payload)[:1000] if isinstance(e.payload, str) else json.dumps(e.payload)[:1000]}"
            for e in entries
        ]
        combined_logs = "\n---\n".join(log_texts)

        # Truncate combined logs to ~3000 tokens (approx 12000 chars) to stay within 4096 context limit
        if len(combined_logs) > 12000:
            combined_logs = combined_logs[:12000] + "... (truncated)"

        # Prepare prompt for Gemma
        prompt = f"Analyze the following DevOps logs and provide a high-level summary of the critical issues and potential root causes:\n\n{combined_logs}\n\nSummary:"

        # Query Self-Hosted vLLM (OpenAI compatible API)
        token = get_auth_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        vllm_url = get_vllm_url()
        response = requests.post(
            f"{vllm_url}/v1/completions",
            headers=headers,
            json={
                "model": f"/mnt/models/{MODEL_NAME.split('/')[-1]}",  # Match the path in Cloud Run
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        result = response.json()

        return f"### Log Analysis (Self-Hosted vLLM)\n\n{result['choices'][0]['text']}"

    except Exception as e:
        return f"Error analyzing logs via self-hosted vLLM: {str(e)}"


@mcp.tool()
async def suggest_sre_remediation(error_message: str) -> str:
    """
    Proposes remediation steps for a specific SRE incident using self-hosted vLLM.

    Args:
        error_message: The error or incident description to remediate.
    """
    prompt = f"As an expert SRE, suggest a 3-step remediation plan for the following error:\n\nError: {error_message}\n\nRemediation Plan:"

    try:
        token = get_auth_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        vllm_url = get_vllm_url()
        response = requests.post(
            f"{vllm_url}/v1/completions",
            headers=headers,
            json={
                "model": f"/mnt/models/{MODEL_NAME.split('/')[-1]}",
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        result = response.json()
        return f"### Remediation Plan\n\n{result['choices'][0]['text']}"
    except Exception as e:
        return f"Error fetching remediation plan: {str(e)}"


@mcp.tool()
async def query_vllm(prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
    """
    Directly queries the self-hosted vLLM model with a custom prompt.

    Args:
        prompt: The text prompt to send to the model.
        max_tokens: Maximum number of tokens to generate.
        temperature: Sampling temperature (0.0 for deterministic).
    """
    try:
        token = get_auth_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        vllm_url = get_vllm_url()
        response = requests.post(
            f"{vllm_url}/v1/completions",
            headers=headers,
            json={
                "model": f"/mnt/models/{MODEL_NAME.split('/')[-1]}",
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()
        result = response.json()
        return f"### vLLM Response\n\n{result['choices'][0]['text']}"
    except Exception as e:
        return f"Error querying vLLM: {str(e)}"


@mcp.tool()
def get_vllm_deployment_config(
    service_name: str = "vllm-gemma-4-e4b-it",
    bucket_name: str = BUCKET_NAME,
    model_path: str = "gemma-4-E4B-it",
    allow_unauthenticated: bool = False,
    min_instances: int = 0,
    gpu_memory_utilization: float = 0.9,
) -> str:
    """
    Generates the gcloud command to deploy vLLM to Cloud Run with GCS FUSE and NVIDIA L4 GPU.

    Args:
        service_name: The name for the Cloud Run service.
        bucket_name: The GCS bucket containing the model weights.
        model_path: The sub-path inside the bucket (e.g., 'gemma-4-E4B-it') or Hugging Face repo ID.
        allow_unauthenticated: Whether to allow unauthenticated access to the service.
        min_instances: The minimum number of instances to keep warm (default: 0).
        gpu_memory_utilization: The fraction of GPU memory to use for KV cache (default: 0.9).
    """
    # Check if we are pulling directly from Hugging Face
    is_hf = "/" in model_path and not model_path.startswith("/")

    command = [
        "gcloud beta run deploy",
        service_name,
        "--image=vllm/vllm-openai:latest",
        "--gpu=1",
        "--gpu-type=nvidia-l4",
        "--no-gpu-zonal-redundancy",  # Fix for quota issues in us-east4
        "--no-cpu-throttling",  # Required for GPU deployment
        "--concurrency=4",  # Optimal for LLM throughput vs latency
        "--timeout=3600",  # 1 hour timeout for long generations
        "--startup-probe=timeoutSeconds=60,periodSeconds=60,failureThreshold=10,initialDelaySeconds=180,httpGet.port=8000,httpGet.path=/health",
        "--max-instances=1",  # Prevent scaling beyond quota
        f"--min-instances={min_instances}",
        "--port=8000",  # vLLM default port
        "--memory=16Gi",
        "--cpu=4",
        "--execution-environment=gen2",
    ]

    if is_hf:
        command.append("--set-secrets=HF_TOKEN=hf-token:latest")
        command.append(
            f"--args=--model={model_path},--max-model-len=4096,--trust-remote-code,--gpu-memory-utilization={gpu_memory_utilization},--host=0.0.0.0"
        )
    else:
        command.append(f"--add-volume=name=model-volume,type=cloud-storage,bucket={bucket_name},readonly=true")
        command.append("--add-volume-mount=volume=model-volume,mount-path=/mnt/models")
        command.append(
            f"--args=--model=/mnt/models/{model_path},--max-model-len=4096,--trust-remote-code,--gpu-memory-utilization={gpu_memory_utilization},--host=0.0.0.0"
        )

    command.append("--allow-unauthenticated" if allow_unauthenticated else "--no-allow-unauthenticated")
    command.append(f"--region={LOCATION}")

    return " ".join(command)


@mcp.tool()
async def deploy_vllm(
    service_name: str = "vllm-gemma-4-e4b-it",
    model_path: str = "gemma-4-E4B-it",
    bucket_name: str = BUCKET_NAME,
) -> str:
    """
    Deploys vLLM to Cloud Run with GPU.

    Args:
        service_name: Name of the service to deploy.
        model_path: Path to the model (GCS folder name or Hugging Face repo ID).
        bucket_name: GCS bucket name (only used if using GCS FUSE).
    """
    is_hf = "/" in model_path and not model_path.startswith("/")

    cmd = [
        "gcloud",
        "beta",
        "run",
        "deploy",
        service_name,
        f"--project={PROJECT_ID}",
        "--image=vllm/vllm-openai:latest",
        "--gpu=1",
        "--gpu-type=nvidia-l4",
        "--no-gpu-zonal-redundancy",
        "--no-cpu-throttling",
        "--concurrency=4",
        "--timeout=3600",
        "--startup-probe=timeoutSeconds=60,periodSeconds=60,failureThreshold=10,initialDelaySeconds=180,httpGet.port=8000,httpGet.path=/health",
        "--max-instances=1",
        "--min-instances=0",
        "--port=8000",
        "--memory=16Gi",
        "--cpu=4",
        "--execution-environment=gen2",
        "--no-allow-unauthenticated",
        f"--region={LOCATION}",
    ]

    if is_hf:
        cmd.append("--set-secrets=HF_TOKEN=hf-token:latest")
        cmd.append(
            f"--args=--model={model_path},--max-model-len=4096,--trust-remote-code,--gpu-memory-utilization=0.9,--host=0.0.0.0"
        )
    else:
        cmd.append(f"--add-volume=name=model-volume,type=cloud-storage,bucket={bucket_name},readonly=true")
        cmd.append("--add-volume-mount=volume=model-volume,mount-path=/mnt/models")
        cmd.append(
            f"--args=--model=/mnt/models/{model_path},--max-model-len=4096,--trust-remote-code,--gpu-memory-utilization=0.9,--host=0.0.0.0"
        )

    try:
        result = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, check=True)
        return f"Successfully deployed {service_name}:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Failed to deploy {service_name}:\nError: {e.stderr}\nOutput: {e.stdout}"


@mcp.tool()
def destroy_vllm(service_name: str = "vllm-gemma-4-e4b-it") -> str:
    """
    Destroys the Cloud Run vLLM service.

    Args:
        service_name: Name of the service to destroy.
    """
    cmd = [
        "gcloud",
        "run",
        "services",
        "delete",
        service_name,
        f"--project={PROJECT_ID}",
        f"--region={LOCATION}",
        "--quiet",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Successfully destroyed {service_name}:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Failed to destroy {service_name}:\nError: {e.stderr}\nOutput: {e.stdout}"


@mcp.tool()
def status_vllm(service_name: str = "vllm-gemma-4-e4b-it") -> str:
    """
    Checks the status of the Cloud Run vLLM service.

    Args:
        service_name: Name of the service to check.
    """
    cmd = [
        "gcloud",
        "run",
        "services",
        "describe",
        service_name,
        f"--project={PROJECT_ID}",
        f"--region={LOCATION}",
        "--format=yaml(status.conditions,status.latestCreatedRevisionName,status.url)",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"### Status for {service_name}:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Failed to get status for {service_name}:\nError: {e.stderr}\nOutput: {e.stdout}"


@mcp.tool()
def update_vllm_scaling(min_instances: int, max_instances: int, service_name: str = "vllm-gemma-4-e4b-it") -> str:
    """
    Updates the scaling configuration (min and max instances) for the Cloud Run vLLM service.

    Args:
        min_instances: The minimum number of instances to keep warm.
        max_instances: The maximum number of instances to scale out to.
        service_name: The name of the Cloud Run service to update.
    """
    cmd = [
        "gcloud",
        "run",
        "services",
        "update",
        service_name,
        f"--min-instances={min_instances}",
        f"--max-instances={max_instances}",
        f"--project={PROJECT_ID}",
        f"--region={LOCATION}",
    ]

    try:
        # We use 'update' which doesn't require a full image/env specification if the service exists
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Successfully updated scaling for {service_name} to min={min_instances}, max={max_instances}.\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Failed to update scaling for {service_name}:\nError: {e.stderr}\nOutput: {e.stdout}"


@mcp.tool()
def get_vllm_tpu_deployment_config(cluster_name: str = "tpu-cluster", model_name: str = "google/gemma-2-9b-it") -> str:
    """
    Generates a GKE manifest and setup instructions for deploying vLLM on TPU v5e.

    Args:
        cluster_name: The name of the GKE cluster.
        model_name: The model identifier (e.g., 'google/gemma-2-9b-it').
    """
    manifest = f"""
### 🌀 vLLM on TPU v5e (GKE Deployment)

To deploy vLLM on TPUs, use the following GKE manifest. This configuration targets a **TPU v5e-8** (8 chips) which is ideal for Gemma 2 9B or 27B.

#### 1. Create a TPU Node Pool (if not exists)
```bash
gcloud container node-pools create tpu-v5e-8 \\
    --cluster={cluster_name} \\
    --location={LOCATION} \\
    --machine-type=ct5lp-hightpu-4t \\
    --tpu-topology=2x4 \\
    --num-nodes=1
```

#### 2. Kubernetes Manifest (vllm-tpu.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-tpu
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm-tpu
  template:
    metadata:
      labels:
        app: vllm-tpu
    spec:
      nodeSelector:
        cloud.google.com/gke-tpu-accelerator: tpu-v5-lite-podslice
        cloud.google.com/gke-tpu-topology: 2x4
      containers:
      - name: vllm-tpu
        image: vllm/vllm-tpu:latest
        resources:
          limits:
            google.com/tpu: "8"
          requests:
            google.com/tpu: "8"
        env:
        - name: VLLM_XLA_CACHE_PATH
          value: "/tmp/vllm_xla_cache"
        command: ["python3", "-m", "vllm.entrypoints.openai.api_server"]
        args:
        - "--model={model_name}"
        - "--tensor-parallel-size=8"
        - "--max-model-len=8192"
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-tpu-service
spec:
  selector:
    app: vllm-tpu
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

#### 3. Deployment Steps
1. Save the YAML above to `vllm-tpu.yaml`.
2. Apply it: `kubectl apply -f vllm-tpu.yaml`.
3. (Optional) If using a private model, ensure a Hugging Face token is provided via secret.
"""
    return manifest


@mcp.tool()
def get_vertex_ai_model_copy_instructions(model_name: str = "gemma-4-E4B-it") -> str:
    """
    Provides instructions and commands to transfer Gemma model artifacts from Vertex AI Model Garden to your GCS bucket.
    """
    instructions = f"""
### 🚀 Transferring {model_name} from Vertex AI Model Garden

To use vLLM with Cloud Storage FUSE without Hugging Face, follow these steps:

1. **Accept Terms:** Go to the Vertex AI Model Garden page for Gemma (https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/335) and click 'Accept' on the license agreement.
2. **Download via Signed URL:** After accepting, the console provides a 'Download' button or a signed URL.
3. **Transfer to GCS:**
   If you have the artifacts locally after downloading from the console, use:
   `gcloud storage cp -r ./model_artifacts/* gs://{BUCKET_NAME}/{model_name}/`

4. **Alternative (Direct GCS Copy):**
   Google occasionally provides a managed GCS path for verified projects. If accessible, you can use:
   `gcloud storage cp -r gs://vertex-ai-models/gemma/{model_name}/* gs://{BUCKET_NAME}/{model_name}/`

Once the artifacts are in your bucket, use `get_vllm_deployment_config` to generate your Cloud Run deployment command.
"""
    return instructions


@mcp.tool()
async def get_huggingfacehub_download_path(
    repo_id: str = "google/gemma-4-E4B-it",
) -> str:
    """
    Returns the local cache path for a Hugging Face model using huggingface_hub.
    Note: This may trigger a download if the model is not already in the cache.
    """
    try:
        from huggingface_hub import snapshot_download

        token = await get_secret() or os.getenv("HF_TOKEN")
        # Run synchronous snapshot_download in a separate thread to avoid blocking the async event loop
        path = await asyncio.to_thread(snapshot_download, repo_id=repo_id, token=token)
        return f"Model '{repo_id}' is available at: {path}"
    except Exception as e:
        return f"Error resolving huggingface_hub path: {str(e)}"


@mcp.tool()
def get_huggingface_model_copy_instructions(
    repo_id: str = "google/gemma-4-E4B-it",
    bucket_name: str = BUCKET_NAME,
) -> str:
    """
    Provides instructions and commands to transfer Gemma model weights from Hugging Face to your GCS bucket.

    Args:
        repo_id: The Hugging Face repo ID (e.g., 'google/gemma-4-E4B-it').
        bucket_name: The target GCS bucket name.
    """
    model_name = repo_id.split("/")[-1]

    instructions = f"""
### 📦 Transferring {model_name} from Hugging Face to GCS

To use Hugging Face weights with vLLM on Cloud Run via GCS FUSE, follow these steps:

#### Option A: Using `huggingface_hub` Python Library (Recommended)
`huggingface_hub` simplifies the download process and can be run directly from python:

1. **Download Model:**
   `python3 -c "from huggingface_hub import snapshot_download; print(snapshot_download('{repo_id}'))"`

2. **Upload to GCS:**
   The command above outputs the local path. Use it to copy the artifacts:
   `gcloud storage cp -r /path/to/downloaded/model/* gs://{bucket_name}/{model_name}/`

#### Option B: Using `huggingface-cli`
1. **Setup Hugging Face CLI:**
   `pip install huggingface_hub`
   `huggingface-cli login`

2. **Download Model Artifacts:**
   `huggingface-cli download {repo_id} --local-dir ./{model_name}`

3. **Upload to GCS Bucket:**
   `gcloud storage cp -r ./{model_name}/* gs://{bucket_name}/{model_name}/`

Once uploaded, you can deploy using:
`get_vllm_deployment_config(model_path="{model_name}")`
"""
    return instructions


@mcp.tool()
def check_gpu_quotas(region: str = LOCATION) -> str:
    """
    Checks GPU quotas for a specific region using gcloud compute regions describe.

    Args:
        region: The Google Cloud region to check quotas for (defaults to LOCATION).
    """
    cmd = [
        "gcloud",
        "compute",
        "regions",
        "describe",
        region,
        f"--project={PROJECT_ID}",
        "--format=json(quotas)",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        quotas = data.get("quotas", [])

        # Filter for GPU quotas
        gpu_quotas = []
        for q in quotas:
            metric = q.get("metric", "")
            if "GPU" in metric or "ACCELERATOR" in metric:
                gpu_quotas.append(f"- **{metric}**:\n  - Limit: `{q.get('limit')}`\n  - Usage: `{q.get('usage')}`")

        if not gpu_quotas:
            return f"No GPU/Accelerator quotas found in region `{region}`. This usually means the quota is 0 or not assigned."

        return f"### 📊 GPU Quotas for region `{region}`\n\n" + "\n".join(gpu_quotas)

    except subprocess.CalledProcessError as e:
        return f"Failed to retrieve GPU quotas for region `{region}`:\nError: {e.stderr}\nOutput: {e.stdout}"
    except Exception as e:
        return f"Error checking GPU quotas: {str(e)}"


if __name__ == "__main__":
    mcp.run()
