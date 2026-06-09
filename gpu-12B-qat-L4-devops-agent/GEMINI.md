# 🤖 Gemini Workspace Context: GPU 12B QAT L4 DevOps Agent

This context guide summarizes the configuration, optimal serving parameters, and capabilities of the self-hosted **Gemma 4 DevOps/SRE Agent** running on **Cloud Run GPU** (NVIDIA L4).

---

## ⚙️ Active Environment Configuration

This agent targets Google Cloud Platform (GCP) deployments utilizing:
- **Project ID**: `aisprint-491218` (configurable via `GOOGLE_CLOUD_PROJECT`)
- **Region**: `us-east4` (configurable via `GOOGLE_CLOUD_LOCATION`)
- **Default Model**: `google/gemma-4-12B-it-qat-w4a16-ct` (configurable via `MODEL_NAME`)
- **GPU Accelerator**: NVIDIA L4 GPU (1 unit) on Cloud Run Gen2
- **Default Cloud Run Service Name**: `gpu-12b-qat-l4-devops-agent`

To serve `google/gemma-4-12B-it-qat-w4a16-ct` using vLLM, you must use the vLLM GitHub Recipes repository or vLLM nightly/source builds. Native support for this compressed-tensors (-ct) Google AI for Developers checkpoint requires specific execution parameters.

### 🚀 Serving Command

Run the server using the native compressed-tensors quantization flag:

```bash
vllm serve google/gemma-4-12B-it-qat-w4a16-ct \
    --quantization compressed_tensors \
    --max-model-len 32768 \
    --tensor-parallel-size 1
```

### ⚙️ Key vLLM Options & Flags

| Flag | Recommended Setting | Purpose |
| :--- | :--- | :--- |
| `--quantization` | `compressed_tensors` | Mandatory for reading the w4a16 ct serialization format. |
| `--max-model-len` | `32768` (or up to `256000`) | Caps the KV-cache allocation. Pinning this tightly reserves VRAM. |
| `--tensor-parallel-size` | `1` | Fits easily onto a single high-end consumer or datacenter GPU (requires approx. 7 GB VRAM). |
| `--enforce-eager` | *(Optional)* | Add if you encounter shape mismatches in Marlin GEMM kernels during the initial forward pass. |

For more details, see:
* [vLLM Google Gemma 4 Recipe](https://github.com/vllm-project/recipes/blob/main/Google/Gemma4.md)
* [Google AI Core Gemma Docs](https://ai.google.dev/gemma/docs/core)

---

## 🎯 Quantization-Aware Training (QAT)

For deployments requiring maximum efficiency with minimal quality compromise, Gemma offers official **Quantization-Aware Training (QAT)** models.

Unlike standard Post-Training Quantization (PTQ), which compresses a fully trained model and can lead to quality degradation, QAT integrates quantization simulation into the training process itself. This allows the model to learn to compensate for the precision loss, resulting in smaller models that perform nearly identically to their high-precision baselines.

### Quick Routing Table

| Target Deployment Engine | Download Suffix | Primary Use Case |
| :--- | :--- | :--- |
| llama.cpp / LM Studio (Local) | `{model-name}-qat-q4_0-gguf` | Zero-setup local deployment on CPU, Apple Silicon, or consumer GPUs. |
| vLLM / SGLang | SERVER: `{model-name}-qat-w4a16-ct`<br>MOBILE: `{model-name}-qat-mobile-ct` | High-throughput inference utilizing 4-bit weights with 16-bit activations. |
| Speculative Decoding | MODEL: `{model-name}-qat-q4_0-unquantized`<br>DRAFTER: `{model-name}-qat-q4_0-unquantized-assistant` | Running a primary model alongside its matching MTP draft model to drastically accelerate token generation. The model must be quantized. |
| Other formats | `{model-name}-qat-q4_0-unquantized` | Unquantized weights for converting to other formats (e.g. MLX) |
| Mobile Deployment (Transformers) | `{model-name}-qat-mobile-transformers` | Edge weights optimized for mobile use cases. They serve as reference for other formats. |

Official QAT collections on Hugging Face:
- **[collections/google/gemma-4-qat-q4-0](https://huggingface.co/collections/google/gemma-4-qat-q4-0)**:
  - **Unquantized QAT Checkpoints (`-unquantized` / `-assistant`):** Half-precision weights extracted directly from the QAT pipeline. These are ideal for custom downstream compilation, research, or running speculative decoding using the assistant draft models. *Available for Gemma 4 E2B, E4B, 12B, 26B A4B, and 31B.*
  - **GGUF (`-gguf`):** Checkpoints available for immediate drop-in compatibility across the local LLM ecosystem. *Available for Gemma 4 E2B, E4B, 12B, 26B A4B, and 31B.*
  - **Compressed Tensors (`-w4a16-ct`):** Serialized natively in the `compressed-tensors` standard for optimized, high-concurrency cloud serving. *Available for Gemma 4 E2B, E4B, 12B, and 31B.*
- **[collections/google/gemma-4-qat-mobile](https://huggingface.co/collections/google/gemma-4-qat-mobile)**:
  - **Mobile-Optimized (`-mobile-transformers` / `-mobile-ct`):** Built on a custom `wNa8o8` schema engineered specifically for mobile hardware limits. It utilizes targeted 2-bit decoding layers, optimized KV caches, and static activations to maximize on-device RAM savings without choking edge processors. *Available for Gemma 4 E2B and E4B.*

All official Gemma 4 QAT checkpoints can also be accessed directly from [Kaggle](https://www.kaggle.com/models/google/gemma-4/transformers).

---

## 🚀 Recommended vLLM Configuration for Gemma 4

To achieve stable and performant Gemma 4 serving with tool/function calling support on NVIDIA L4 GPU, use the following container startup arguments:

```yaml
args:
  - --gpu-memory-utilization
  - "0.97"
  - --kv-cache-dtype
  - nvfp4
  - --max-model-len
  - "256000"
  - --tensor-parallel-size
  - "1"
  - --max-num-seqs
  - "8"
  - --enable-chunked-prefill
  - --max-num-batched-tokens
  - "4096"
  - --enable-auto-tool-choice
  - --tool-call-parser
  - gemma4
  - --reasoning-parser
  - gemma4
  - --async-scheduling
  - --limit-mm-per-prompt
  - '{"image": 0, "audio": 0, "video": 0}'
  - --host
  - 0.0.0.0
  - --port
  - "8080"
```

### Key Parameters Explained
*   **`--gpu-memory-utilization 0.97`**: Allocates 97% of VRAM to vLLM's KV cache.
*   **`--kv-cache-dtype nvfp4`**: Uses nvfp4 for 4-bit KV cache, reducing memory consumption and increasing capacity.
*   **`--tool-call-parser gemma4` & `--reasoning-parser gemma4`**: Essential settings for correct parsing of tool calls and structured reasoning steps generated by Gemma 4.
*   **`--enable-auto-tool-choice`**: Prompts the model to automatically select registered tools.
*   **`--max-model-len 256000`**: Maximum sequence length capability optimized for long-context operations.

---

## 🧰 Key SRE & DevOps Capabilities

This agent exposes several tool categories via the Model Context Protocol (MCP):
- **Deployment & Scaling:** 
  - [deploy_vllm](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L459)
  - [destroy_vllm](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L524)
  - [status_vllm](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L550)
  - [update_vllm_scaling](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L576)
  - [get_vllm_deployment_config](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L393)
  - [get_vllm_gpu_deployment_config](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L606)
  - [check_gpu_quotas](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L783)
  - [get_vllm_endpoint](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L237)
- **Model Transfer & Secret Management:** 
  - [list_vertex_models](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L251)
  - [list_bucket_models](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L267)
  - [save_hf_token](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L49)
  - [get_vertex_ai_model_copy_instructions](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L693)
  - [get_huggingface_model_copy_instructions](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L737)
  - [get_huggingfacehub_download_path](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L718)
- **System Monitoring & Health:** 
  - [get_system_status](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L974)
  - [get_endpoint](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L1042)
  - [get_model_details](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L935)
  - [verify_model_health](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L824)
- **Performance Benchmarking:** 
  - [run_benchmark](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L1066)
- **Diagnostics & SRE Remediation:** 
  - [query_gemma4](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L853)
  - [query_gemma4_with_stats](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L872)
  - [query_vllm](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L368)
  - [analyze_cloud_logging](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L297)
  - [analyze_gpu_logs](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L1215)
  - [suggest_sre_remediation](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L343)
  - [get_help](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py#L1228)

---

## 🛠 Command Line Setup

### Deploy/Run Quickstart
```bash
# 1. Install dependencies
make install

# 2. Deploy vLLM to Cloud Run (with NVIDIA L4)
make deploy

# 3. Check deployment status
make status

# 4. Start the MCP server locally
make run
```

---

## 📚 Key Source Code File Locations
- **MCP Server entrypoint**: [server.py](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py)
- **Deployment Manifests & Logic**: Generated by `get_vllm_deployment_config` and `get_vllm_gpu_deployment_config` in [server.py](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/server.py).
- **Test Suite**: [test_agent.py](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/test_agent.py)
- **Standalone Grand Demo**: [demo_launcher.py](file:///home/xbill/gemma4-tips/gpu-12B-qat-L4-devops-agent/demo_launcher.py)
