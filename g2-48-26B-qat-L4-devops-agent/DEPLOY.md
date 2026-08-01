# Deployment Guide: Self-Hosted vLLM on GCP GCE (Gemma 4 31B-it QAT)

This document summarizes the deployment state, configuration, and architecture for the self-hosted vLLM inference server running on Google Compute Engine (GCE).

---

## 📦 Model Artifacts
The model is served using the official quantized w4a16 compressed-tensors (QAT) checkpoint:
*   **Source:** Hugging Face (`google/gemma-4-31B-it-qat-w4a16-ct`)
*   **Alternative Storage:** Google Cloud Storage (GCS) Bucket
*   **Format:** Hugging Face Transformers (Safetensors with compressed-tensors)

---

## 🚀 GCP GCE Inference Stack (g2-standard-48 Spot VM)
The inference server is sharded across 4x NVIDIA L4 GPUs on a single GCP GCE Spot VM for maximum cost efficiency and performance.

*   **Instance Type:** `g2-standard-48`
*   **Provisioning Model:** Spot VM (cost-optimized)
*   **GPU Accelerator:** 4x NVIDIA L4 (96 GiB total VRAM)
*   **vCPUs / RAM:** 48 vCPUs / 192 GiB RAM
*   **Operating System / Image:** Deep Learning VM Image with CUDA preinstalled (e.g. `common-cu129-ubuntu-2204-nvidia-580`)
*   **Container Port:** `8080` (mapped to Host Port `8080`)
*   **Firewall Rules:** Allow inbound TCP on `8080` and `22` (SSH)

### GCP CLI Launch Command (Spot)
```bash
gcloud compute instances create gpu-31b-qat-l4-devops-agent \
  --project=aisprint-491218 \
  --zone=europe-west1-c \
  --machine-type=g2-standard-48 \
  --accelerator=type=nvidia-l4,count=4 \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --maintenance-policy=TERMINATE \
  --image-family=common-cu129-ubuntu-2204-nvidia-580 \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=150GB \
  --boot-disk-type=pd-balanced \
  --metadata-from-file=startup-script=startup_script.sh \
  --tags=vllm-server
```

---

## 🛠 Deployment & Startup Script

The GCE instance is deployed with a startup script that automatically installs Docker, configures GSecret Access, and launches the vLLM engine inside a container with optimized parameters.

### startup_script.sh
```bash
#!/bin/bash
if ! command -v docker &> /dev/null; then
    apt-get update -y
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
fi
docker run -d --name vllm-server \
  --gpus all \
  --ipc=host \
  --restart always \
  -p 8080:8080 \
  -e HF_TOKEN="$(gcloud secrets versions access latest --secret=hf-token 2>/dev/null || echo '')" \
  vllm/vllm-openai:nightly \
  --model google/gemma-4-31B-it-qat-w4a16-ct \
  --quantization compressed-tensors \
  --dtype bfloat16 \
  --max-model-len 32768 \
  --disable-chunked-mm-input \
  --gpu-memory-utilization 0.95 \
  --kv-cache-dtype fp8 \
  --tensor-parallel-size 4 \
  --max-num-seqs 8 \
  --enable-chunked-prefill \
  --max-num-batched-tokens 4096 \
  --enable-auto-tool-choice \
  --tool-call-parser gemma4 \
  --reasoning-parser gemma4 \
  --async-scheduling \
  --limit-mm-per-prompt '{}' \
  --host 0.0.0.0 \
  --port 8080
```

---

## 🔗 Integration with SRE Agent
To connect the MCP SRE Agent to the newly deployed GCP VM endpoint:

1. Discover the external IP of your GCE instance:
   ```bash
   gcloud compute instances describe gpu-31b-qat-l4-devops-agent \
     --zone=europe-west1-c \
     --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
   ```
2. Export the endpoint URL in your terminal environment:
   ```bash
   export VLLM_BASE_URL="http://<instance-external-ip>:8080"
   export MODEL_NAME="google/gemma-4-31B-it-qat-w4a16-ct"
   ```
3. Start the agent:
   ```bash
   make run
   ```
