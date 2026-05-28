# Gemma 4 Local DevOps Agent Tools

This document summarizes the MCP tools available in [server.py](file:///home/xbill/gemma4-tips/local-devops-agent/server.py) for the Local Gemma 4 SRE Agent.

## Deployment & Configuration

-   **[manage_docker](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L125)**: Manages the local vLLM/Ollama Docker container (actions: `start`, `stop`, `restart`, `status`, `log`, `rm`).
-   **[save_hf_token](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L111)**: Securely saves a Hugging Face API token locally in environment variables and cache.

## Monitoring & Status

-   **[get_system_status](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L160)**: Provides a high-level status dashboard of the local Docker container and vLLM service.
-   **[get_endpoint](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L194)**: Verifies connectivity and returns the active local vLLM service URL.
-   **[get_help](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L411)**: Provides help text and summarizes the configuration options and available tools.

## Performance & Benchmarking

-   **[run_vllm_benchmark](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L284)**: Runs vLLM's internal serving benchmark tool inside the local container.
-   **[get_docker_logs](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L352)**: Retrieves startup and execution logs from the local Docker container.
-   **[analyze_local_logs](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L364)**: Fetches the local container logs and uses Gemma 4 to analyze them for SRE/DevOps errors.

## Interaction & Diagnostics

-   **[query_gemma4](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L205)**: Queries the self-hosted local model.
-   **[query_gemma4_with_stats](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L223)**: Queries the local model and provides streaming-based performance metrics (TTFT, throughput, latency).
-   **[verify_model_health](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L84)**: Performs a health check by querying the model with a simple prompt and measuring response latency.
-   **[get_model_details](file:///home/xbill/gemma4-tips/local-devops-agent/server.py#L383)**: Retrieves detailed information about the running local model, engine, and versions.
