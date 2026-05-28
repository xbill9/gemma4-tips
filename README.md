# 🚀 Gemma 4 DevOps Agents

Welcome to the **Gemma-4 DevOps Agents** workspace. This repository contains three specialized, self-hosted AI-driven DevOps/SRE agents powered by Google's **Gemma 4** model. These agents are packaged as Model Context Protocol (MCP) servers to analyze, monitor, and troubleshoot infrastructure components.

---

## 📂 Project Structure

This workspace is organized into three distinct sub-agents, each tailored to a specific environment and serving stack:

| Sub-Agent | Purpose | Serving Engine | Target Infrastructure |
| :--- | :--- | :--- | :--- |
| [Local DevOps Agent](file:///home/xbill/gemma4-tips/local-devops-agent) | CPU/GPU local analysis & prototyping | Ollama / vLLM | Local Docker / Workstations |
| [GPU DevOps Agent](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent) | Serverless GPU-accelerated cloud analysis | vLLM | Google Cloud Run (NVIDIA L4 GPU) |
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
  - [manage_docker](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L125): Manage the local container.
  - [analyze_local_logs](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L364): Automated log diagnostic reports.
  - [query_gemma4_with_stats](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L223): Measure local inference latency and throughput.
- **Documentation:** See [local-devops-agent/README.md](file:///home/xbill/gemma4-tips/local-devops-agent/README.md) and [local-devops-agent/GEMINI.md](file:///home/xbill/gemma4-tips/local-devops-agent/GEMINI.md).

### 2. [GPU DevOps Agent](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent)
- **Role:** Cloud-based SRE managing GPU-accelerated serverless endpoints.
- **Inference Stack:** Runs `google/gemma-4-E4B-it` (or other variants) via vLLM on GCP Cloud Run (NVIDIA L4 GPU).
- **Key Tools:**
  - `deploy_vllm`: Automates serverless Cloud Run GPU vLLM deployments.
  - `analyze_cloud_logging`: Summarizes Google Cloud Logging errors.
  - `get_vllm_deployment_config`: Generates `gcloud` configuration options.
- **Documentation:** See [gpu-vllm-devops-agent/README.md](file:///home/xbill/gemma4-tips/gpu-vllm-devops-agent/README.md).

### 3. [TPU DevOps Agent](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent)
- **Role:** High-performance TPU SRE/DevOps managing large-scale private clusters.
- **Inference Stack:** Runs `google/gemma-4-31B-it` via vLLM on Google Cloud TPUs (v6e Trillium / Flex-start VMs).
- **Key Tools:**
  - `orchestrate_gemma4_stack`: Automatic setup of TPU Queued Resources and vLLM deployments.
  - `check_tpu_utilization`: Monitors HBM and Tensor Core performance via logs.
  - `run_load_test_benchmark`: Simulates load and tracks performance stats.
- **Documentation:** See [tpu-vllm-devops-agent/README.md](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/README.md) and [tpu-vllm-devops-agent/GEMINI.md](file:///home/xbill/gemma4-tips/tpu-vllm-devops-agent/GEMINI.md).

---

## 🔒 Security & Credentials
When deploying to Google Cloud or Hugging Face, secure credentials using:
- **Hugging Face Access Token:** Saved locally or to Google Secret Manager via `save_hf_token` tools.
- **Application Default Credentials (ADC):** Set up using GCP credentials helper scripts (`set_adc.sh` inside individual sub-agent folders).
