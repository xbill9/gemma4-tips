#!/bin/bash
set -ex

# Setup environment
export HF_HOME=/dev/shm
export HF_TOKEN=$(gcloud secrets versions access latest --secret=hf-token)
export VLLM_TPU_BUCKET_PADDING_GAP=512
export VLLM_XLA_CACHE_PATH=/dev/shm/vllm_cache

# Docker run command
sudo docker stop vllm-gemma4 > /dev/null 2>&1 || true
sudo docker rm vllm-gemma4 > /dev/null 2>&1 || true

sudo docker run --name vllm-gemma4 --privileged --net=host -d \
  -v /dev/shm:/dev/shm -v /home/xbill/run_patched_vllm.py:/run_patched_vllm.py --shm-size 10gb \
  -e HF_HOME="$HF_HOME" \
  -e HF_TOKEN="$HF_TOKEN" \
  -e VLLM_TPU_BUCKET_PADDING_GAP="$VLLM_TPU_BUCKET_PADDING_GAP" \
  -e VLLM_XLA_CACHE_PATH="$VLLM_XLA_CACHE_PATH" \
  -e JAX_TPU_MEM_FRACTION=0.95 \
  vllm/vllm-tpu:nightly /bin/bash -c '
    pip install git+https://github.com/huggingface/transformers.git "fastapi<0.112" && \
    python3 /run_patched_vllm.py serve vrfai/gemma-4-12B-it-fp8 \
      --quantization fp8 \
      --tensor-parallel-size 1 \
      --dtype bfloat16 \
      --kv-cache-dtype fp8 \
      --gpu-memory-utilization 0.85 \
      --block-size 32 \
      --disable_chunked_mm_input \
      --max-model-len 18432 \
      --trust-remote-code \
      --max-num-batched-tokens 4096 \
      --enable-auto-tool-choice \
      --tool-call-parser gemma4 \
      --reasoning-parser gemma4 \
      --enable-prefix-caching \
      --max-num-seqs 32 \
      --limit-mm-per-prompt '\''{"image":4,"audio":1}'\''
  '
