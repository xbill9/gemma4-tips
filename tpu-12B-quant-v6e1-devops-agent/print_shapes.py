import os
import sys

# Force CPU/JAX mock to inspect model architecture without requiring TPU device
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["HF_TOKEN"] = "none"

try:
    from vllm.config import ModelConfig, ParallelConfig, DeviceConfig, LoadConfig
    from vllm.model_executor.model_loader.weight_utils import get_model_architecture
    import torch
except ImportError as e:
    print(f"Failed to import vllm: {e}")
    sys.exit(1)

model_id = "/dev/shm/hub/models--vrfai--gemma-4-12B-it-fp8/snapshots/fa2f3eacc4315467cc1f7ff3ceab216224b78ebb"

print("Initializing ModelConfig...")
model_config = ModelConfig(
    model=model_id,
    tokenizer=model_id,
    tokenizer_mode="auto",
    trust_remote_code=True,
    dtype="bfloat16",
    seed=0,
    quantization="fp8",
)

device_config = DeviceConfig(device_type="cpu")
parallel_config = ParallelConfig(tensor_parallel_size=1, pipeline_parallel_size=1)
load_config = LoadConfig()

print("Resolving model architecture...")
model_class, archs = get_model_architecture(model_config)
print("Model class resolved:", model_class)

# Let's inspect the weights mapper or model initialization parameters if possible.
# Since we just want to see the parameter shapes for layer 5 MLP, let's instantiate the model if it doesn't require device.
try:
    print("Instantiating model on CPU...")
    # JAX model on CPU might require jax initialization.
    import jax
    jax.config.update("jax_platform_name", "cpu")
    
    # We can instantiate the model class
    # Model class initialization signature: model_class(config=model_config.hf_config, cache_config=None, quant_config=model_config.quant_config)
    # Let's check quant_config
    print("Quantization config:", model_config.quant_config)
    
    # Let's load the model and catch the assertion error by printing parameter details
    from safetensors.torch import load_file
    import glob
    
    # Load one of the model files to check target weights
    checkpoint_files = glob.glob(os.path.join(model_id, "*.safetensors"))
    weights = {}
    for f in checkpoint_files:
        weights.update(load_file(f))
        
    print("Checkpoint loaded.")
    
    # Let's print out the keys and shapes that have "weight" in their name and "layers.5.mlp"
    for k, v in weights.items():
        if "layers.5.mlp" in k:
            print(f"Checkpoint Weight: {k} -> shape: {v.shape}, dtype: {v.dtype}")
            
except Exception as e:
    print(f"Failed during model inspection: {e}")
    import traceback
    traceback.print_exc()
