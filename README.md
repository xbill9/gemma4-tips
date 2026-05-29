# 🚀 Gemma 4 DevOps Agents

Welcome to the **Gemma-4 DevOps Agents** workspace. This repository contains three specialized, self-hosted AI-driven DevOps/SRE agents powered by Google's **Gemma 4** model. These agents are packaged as Model Context Protocol (MCP) servers to analyze, monitor, and troubleshoot infrastructure components.

---

## 📂 Project Structure

This workspace is organized into five distinct sub-agents, each tailored to a specific environment and serving stack:

| Sub-Agent | Purpose | Serving Engine | Target Infrastructure |
| :--- | :--- | :--- | :--- |
| [Local DevOps Agent](file:///home/xbill/gemma4-tips/local-devops-agent) | CPU/GPU local analysis & prototyping | Ollama / vLLM | Local Docker / Workstations |
| [GPU DevOps Agent (26B)](file:///home/xbill/gemma4-tips/gpu-26B-devops-agent) | Serverless GPU-accelerated cloud analysis (26B config) | vLLM | Google Cloud Run (us-central1) |
| [GPU DevOps Agent (6000)](file:///home/xbill/gemma4-tips/gpu-6000-devops-agent) | Serverless GPU-accelerated cloud analysis (RTX 6000) | vLLM | Google Cloud Run (us-central1) |
| [GPU DevOps Agent (vLLM)](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent) | Serverless GPU-accelerated cloud analysis (L4 GPU) | vLLM | Google Cloud Run (us-east4) |
| [TPU DevOps Agent](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent) | Ultra-high performance enterprise log & infra analysis | vLLM | Google Cloud TPUs (v6e Trillium) |

---

## 🛠 Features & Capabilities

- **Automated SRE Diagnostics:** Fetches and reviews system, container, and Cloud Logging entries using Gemma 4 to identify root causes and generate 3-step remediation plans.
- **Serving Stack Control:** Built-in tools to provision, start, stop, restart, and scale your vLLM and Ollama containers or Cloud TPU Queued Resources.
- **Observability Dashboards:** Real-time dashboards monitoring HBM usage, Tensor Core pressure, Prometheus metrics, and service latencies.
- **Model Benchmarking:** Tools to run load tests and vLLM's internal benchmark suites, returning performance metrics (TTFT, throughput, P95 latency).
- **Gemini CLI Integration:** Custom setup instructions using a LiteLLM Proxy to route standard Gemini CLI commands directly to your private, self-hosted Gemma 4 instance.

---

## 🏗 Global Makefile Usage

A root [Makefile](file:///home/xbill/gemma4-tips/Makefile) is provided to manage the sub-agents collectively:

- **Help / Display commands:**
  ```bash
  make all
  ```
- **Install dependencies in all subdirectories:**
  ```bash
  make install
  ```
- **Run tests across all agents:**
  ```bash
  make test
  ```
- **Lint all Python directories:**
  ```bash
  make lint
  ```
- **Clean build/cache folders:**
  ```bash
  make clean
  ```

---

## 🚀 Sub-Agent Overviews

### 1. [Local DevOps Agent](file:///home/xbill/gemma4-tips/local-devops-agent)
- **Role:** Specialized SRE specialized in local containerized workloads.
- **Inference Stack:** Runs `gemma4:e2b` or `google/gemma-4-E2B-it` via local Docker (`ollama/ollama` or CPU/GPU vLLM).
- **Key Tools:**
  - [manage_docker](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L127): Manage the local container.
  - [analyze_local_logs](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L371): Automated log diagnostic reports.
  - [query_gemma4_with_stats](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L225): Measure local inference latency and throughput.
  - [get_help](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L418): Retrieve server configuration and tool details.
- **Documentation:** See [local-devops-agent/README.md](file:///home/xbill/gemma4-tips/local-devops-agent/README.md) and [local-devops-agent/GEMINI.md](file:///home/xbill/gemma4-tips/local-devops-agent/GEMINI.md).

### 2. [GPU DevOps Agent (26B)](file:///home/xbill/gemma4-tips/gpu-26B-devops-agent)
- **Role:** Cloud-based SRE managing GPU-accelerated serverless endpoints (26B configuration).
- **Inference Stack:** Runs `google/gemma-4-26B-A4B-it` via vLLM on GCP Cloud Run (RTX 6000 GPU in us-central1).
- **Key Tools:**
  - [deploy_vllm](file:///home/xbill/gemma4-tips/gpu-26B-devops-agent/server.py#L480): Automates serverless Cloud Run GPU vLLM deployments.
  - [analyze_cloud_logging](file:///home/xbill/gemma4-tips/gpu-26B-devops-agent/server.py#L340): Summarizes Google Cloud Logging errors.
  - [get_vllm_deployment_config](file:///home/xbill/gemma4-tips/gpu-26B-devops-agent/server.py#L390): Generates `gcloud` configuration options.
  - [get_help](file:///home/xbill/gemma4-tips/gpu-26B-devops-agent/server.py#L1274): Retrieve server configuration and tool details.
- **Documentation:** See [gpu-26B-devops-agent/README.md](file:///home/xbill/gemma4-tips/gpu-26B-devops-agent/README.md).

### 3. [GPU DevOps Agent (6000)](file:///home/xbill/gemma4-tips/gpu-6000-devops-agent)
- **Role:** Cloud-based SRE managing GPU-accelerated serverless endpoints (RTX 6000 config).
- **Inference Stack:** Runs `google/gemma-4-26B-A4B-it` via vLLM on GCP Cloud Run (RTX 6000 GPU in us-central1).
- **Key Tools:**
  - [deploy_vllm](file:///home/xbill/gemma4-tips/gpu-6000-devops-agent/server.py#L455): Automates serverless Cloud Run GPU vLLM deployments.
  - [analyze_cloud_logging](file:///home/xbill/gemma4-tips/gpu-6000-devops-agent/server.py#L295): Summarizes Google Cloud Logging errors.
  - [get_vllm_deployment_config](file:///home/xbill/gemma4-tips/gpu-6000-devops-agent/server.py#L391): Generates `gcloud` configuration options.
  - [get_help](file:///home/xbill/gemma4-tips/gpu-6000-devops-agent/server.py#L1223): Retrieve server configuration and tool details.
- **Documentation:** See [gpu-6000-devops-agent/README.md](file:///home/xbill/gemma4-tips/gpu-6000-devops-agent/README.md).

### 4. [GPU DevOps Agent (vLLM)](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent)
- **Role:** Cloud-based SRE managing GPU-accelerated serverless endpoints (L4 configuration).
- **Inference Stack:** Runs `google/gemma-4-E4B-it` via vLLM on GCP Cloud Run (NVIDIA L4 GPU in us-east4).
- **Key Tools:**
  - [deploy_vllm](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent/server.py#L455): Automates serverless Cloud Run GPU vLLM deployments.
  - [analyze_cloud_logging](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent/server.py#L295): Summarizes Google Cloud Logging errors.
  - [get_vllm_deployment_config](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent/server.py#L391): Generates `gcloud` configuration options.
  - [get_help](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent/server.py#L1223): Retrieve server configuration and tool details.
- **Documentation:** See [gpu-vllm-devops-agent/README.md](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent/README.md).

### 5. [TPU DevOps Agent](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent)
- **Role:** High-performance TPU SRE/DevOps managing large-scale private clusters.
- **Inference Stack:** Runs `google/gemma-4-31B-it` via vLLM on Google Cloud TPUs (v6e Trillium / Flex-start VMs).
- **Key Tools:**
  - [manage_queued_resource](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/server.py#L299): Manage the TPU Queued Resource (create, check, etc.).
  - [run_vllm_benchmark](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/server.py#L667): Run performance benchmark on TPU.
  - [query_queued_gemma4_with_stats](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/server.py#L606): Query model on TPU and measure latency/throughput.
  - [get_help](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/server.py#L913): Retrieve server configuration and tool details.
- **Documentation:** See [tpu-vllm-devops-agent/README.md](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/README.md) and [tpu-vllm-devops-agent/GEMINI.md](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/GEMINI.md).

---

## 🔒 Security & Credentials
When deploying to Google Cloud or Hugging Face, secure credentials using:
- **Hugging Face Access Token:** Saved locally or to Google Secret Manager via `save_hf_token` tools.
- **Application Default Credentials (ADC):** Set up using GCP credentials helper scripts (`set_adc.sh` inside individual sub-agent folders).
