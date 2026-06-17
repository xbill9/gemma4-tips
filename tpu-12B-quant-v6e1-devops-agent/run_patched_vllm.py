import os
fp8_path = "/workspace/tpu_inference/tpu_inference/layers/vllm/quantization/fp8.py"
if os.path.exists(fp8_path):
    print("Found JAX FP8 file, applying patches...", flush=True)
    with open(fp8_path, "r") as f:
        code = f.read()
    
    old_line = "if self.linear_config.fuse_matmuls and weight_scale.ndim == 1:"
    new_line = "if self.linear_config.fuse_matmuls and weight_scale.ndim == 1 and weight_scale.shape[0] == len(self.linear_config.output_sizes):"
    if old_line in code:
        code = code.replace(old_line, new_line)
        print("PATCHED JAX FP8.PY REPLICATION CONDITION SUCCESS", flush=True)
    
    target_str = "weight_scale = t2j(weight_scale, use_dlpack=False)"
    if target_str in code:
        replacement_str = """if weight_scale.ndim > 1:
                print(f"DEBUG: Flattening weight_scale with shape {weight_scale.shape}", flush=True)
                weight_scale = weight_scale.flatten()
            weight_scale = t2j(weight_scale, use_dlpack=False)"""
        code = code.replace(target_str, replacement_str)
        print("PATCHED JAX FP8.PY FLATTENING SUCCESS", flush=True)
        
    print("--- START OF fp8.py ---", flush=True)
    print(code, flush=True)
    print("--- END OF fp8.py ---", flush=True)

    with open(fp8_path, "w") as f:
        f.write(code)

linear_path = "/workspace/tpu_inference/tpu_inference/layers/common/linear.py"
if os.path.exists(linear_path):
    print("Found JAX linear.py file, applying patches to disable activation quantization...", flush=True)
    with open(linear_path, "r") as f:
        code = f.read()
    
    old_def = "def xla_quantized_matmul(\n    x: jax.Array,\n    w_q: jax.Array,\n    w_scale: jax.Array,\n    quantize_activation=True,\n)"
    new_def = "def xla_quantized_matmul(\n    x: jax.Array,\n    w_q: jax.Array,\n    w_scale: jax.Array,\n    quantize_activation=False,\n)"
    if old_def in code:
        code = code.replace(old_def, new_def)
        print("PATCHED linear.py def xla_quantized_matmul SUCCESS", flush=True)
    else:
        code = code.replace("quantize_activation=True,", "quantize_activation=False,")
        print("PATCHED linear.py quantize_activation=True SUCCESS (fallback)", flush=True)

    old_act = "_should_quantize_act = x.dtype.itemsize > 1"
    new_act = "_should_quantize_act = False"
    if old_act in code:
        code = code.replace(old_act, new_act)
        print("PATCHED linear.py sharded_quantized_batched_matmul act SUCCESS", flush=True)
        
    with open(linear_path, "w") as f:
        f.write(code)

import sys
import torch
import vllm.model_executor.parameter
import vllm.model_executor.models.gemma4_unified

# Patch weight mapping to handle multimodal_embedder and vision_embedder parameters correctly
old_prefixes = vllm.model_executor.models.gemma4_unified.Gemma4UnifiedForConditionalGeneration.hf_to_vllm_mapper.orig_to_new_prefix
new_prefixes = {
    "model.embed_vision.patch_dense.": "vision_embedder.patch_dense.",
    "model.embed_vision.patch_ln1.": "vision_embedder.patch_ln1.",
    "model.embed_vision.patch_ln2.": "vision_embedder.patch_ln2.",
    "model.embed_vision.pos_embedding": "vision_embedder.pos_embedding",
    "model.embed_vision.pos_norm.": "vision_embedder.pos_norm.",
    "model.embed_vision.multimodal_embedder.": "embed_vision.",
    "model.embed_audio.multimodal_embedder.": "embed_audio.",
}
new_prefixes.update(old_prefixes)
vllm.model_executor.models.gemma4_unified.Gemma4UnifiedForConditionalGeneration.hf_to_vllm_mapper.orig_to_new_prefix = new_prefixes

original_assert_and_load = vllm.model_executor.parameter.BasevLLMParameter._assert_and_load
original_load_into_shard_id = vllm.model_executor.parameter.PerTensorScaleParameter._load_into_shard_id

def patched_assert_and_load(self, loaded_weight: torch.Tensor):
    class_name = self.__class__.__name__
    if self.data.shape != loaded_weight.shape and not self._is_1d_and_scalar(loaded_weight):
        if "Scale" in class_name or "scale" in class_name:
            print(f"DEBUG: Resizing {class_name} from {self.data.shape} to {loaded_weight.shape} to accommodate loaded scale", flush=True)
            self.data = torch.empty(loaded_weight.shape, dtype=self.data.dtype, device=self.data.device)
        else:
            print("\n" + "="*80, flush=True)
            print("SHAPE MISMATCH DETECTED DURING WEIGHT LOADING:", flush=True)
            print(f"  Expected parameter shape: {self.data.shape}", flush=True)
            print(f"  Loaded weight shape:      {loaded_weight.shape}", flush=True)
            print("="*80 + "\n", flush=True)
            assert False, f"Shape mismatch for non-scale parameter: expected {self.data.shape}, got {loaded_weight.shape}"
    self.data.copy_(loaded_weight)

def patched_load_into_shard_id(self, loaded_weight: torch.Tensor, shard_id: str | int, **kwargs):
    class_name = self.__class__.__name__
    shard_id = self._shard_id_as_int(shard_id)
    
    if ("Scale" in class_name or "scale" in class_name) and len(loaded_weight.shape) != 0 and loaded_weight.shape[0] > 1:
        # Per-channel scales loaded into sharded parameters (like QKV scales)
        if self.data.ndim == 1:
            num_shards = self.data.shape[0]
            shard_channel_size = loaded_weight.shape[0]
            print(f"DEBUG: Resizing 1D scale parameter {class_name} from {self.data.shape} to 2D [{num_shards}, {shard_channel_size}]", flush=True)
            self.data = torch.empty((num_shards, shard_channel_size), dtype=self.data.dtype, device=self.data.device)
        
        self.data[shard_id].copy_(loaded_weight)
        return

    try:
        if len(loaded_weight.shape) != 0:
            if loaded_weight.shape[0] == 1:
                loaded_weight = loaded_weight[0]
            else:
                print(f"WARNING: loaded_weight.shape is {loaded_weight.shape} for parameter {self} (class {class_name})", flush=True)
        
        param_data = self.data[shard_id]
        assert param_data.shape == loaded_weight.shape or self._is_1d_and_scalar(loaded_weight)
        param_data.copy_(loaded_weight)
    except AssertionError as e:
        print("\n" + "="*80, flush=True)
        print("SHAPE MISMATCH DETECTED DURING SHARD LOADING:", flush=True)
        print(f"  Shard ID:                 {shard_id}", flush=True)
        print(f"  Expected param shard shape: {self.data[shard_id].shape}", flush=True)
        print(f"  Loaded weight shape:        {loaded_weight.shape}", flush=True)
        print(f"  Parameter object:           {self}", flush=True)
        print("="*80 + "\n", flush=True)
        raise e

vllm.model_executor.parameter.BasevLLMParameter._assert_and_load = patched_assert_and_load
vllm.model_executor.parameter.PerTensorScaleParameter._load_into_shard_id = patched_load_into_shard_id

# Start standard vllm CLI entry point
from vllm.entrypoints.cli.main import main
if __name__ == "__main__":
    main()
