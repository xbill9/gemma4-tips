import os
import json
import sys
from huggingface_hub import hf_hub_download

def main():
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN environment variable not set.")
        sys.exit(1)
        
    model_id = "vrfai/gemma-4-12B-it-fp8"
    cache_dir = "/dev/shm/hub"
    
    print("Downloading config.json...")
    try:
        config_path = hf_hub_download(
            repo_id=model_id,
            filename="config.json",
            cache_dir=cache_dir,
            token=token
        )
        print(f"Downloaded config.json to: {config_path}")
    except Exception as e:
        print(f"Failed to download config.json: {e}")
        sys.exit(1)

    # Patch config.json
    with open(config_path, "r") as f:
        config = json.load(f)

    changed = False
    
    # 1. Patch quant_method and add activation_scheme
    quant_config = config.get("quantization_config", {})
    if quant_config.get("quant_method") == "modelopt" or "activation_scheme" not in quant_config:
        print("Changing quant_method to fp8 and adding activation_scheme...")
        quant_config["quant_method"] = "fp8"
        quant_config["activation_scheme"] = "static"
        config["quantization_config"] = quant_config
        changed = True

    # 2. Add missing vision parameters
    if "vision_config" in config:
        if config["vision_config"].get("num_soft_tokens") != 280:
            print("Setting num_soft_tokens to 280...")
            config["vision_config"]["num_soft_tokens"] = 280
            changed = True
        if config["vision_config"].get("model_patch_size") != 48:
            print("Setting model_patch_size to 48...")
            config["vision_config"]["model_patch_size"] = 48
            changed = True
    else:
        print("Adding vision_config with required parameters...")
        config["vision_config"] = {
            "num_soft_tokens": 280,
            "model_patch_size": 48
        }
        changed = True

    if changed:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print("config.json successfully patched!")
    else:
        print("No changes needed for config.json.")

    # 3. Pre-download the rest of the model files
    print("Pre-downloading remaining model files...")
    exit_code = os.system(f"huggingface-cli download {model_id} --cache-dir {cache_dir} --token {token}")
    if exit_code != 0:
        print("Warning: huggingface-cli download returned non-zero exit code.")
    else:
        print("Model downloaded successfully!")

if __name__ == "__main__":
    main()
