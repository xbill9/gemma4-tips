import asyncio
import subprocess
import json
import sys
import time

PROJECT_ID = "aisprint-491218"
ZONE = "europe-west4-a"
RESOURCE_ID = "vllm-gemma4-qr"

def run_cmd(args):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(args)}: {e.stderr}")
        return None

def get_state():
    args = [
        "gcloud", "alpha", "compute", "tpus", "queued-resources", "describe",
        RESOURCE_ID, f"--zone={ZONE}", f"--project={PROJECT_ID}",
        "--format=value(state.state)"
    ]
    return run_cmd(args)

def get_node_ip():
    args = [
        "gcloud", "compute", "tpus", "tpu-vm", "describe",
        f"{RESOURCE_ID}-node", f"--zone={ZONE}", f"--project={PROJECT_ID}",
        "--format=json(networkEndpoints)"
    ]
    stdout = run_cmd(args)
    if not stdout:
        return None
    try:
        data = json.loads(stdout)
        endpoints = data.get("networkEndpoints", [])
        if endpoints:
            # Usually we take the ipAddress of the first endpoint
            return endpoints[0].get("ipAddress")
    except Exception as e:
        print(f"Failed to parse endpoints: {e}")
    return None

async def monitor():
    print(f"Monitoring TPU Queued Resource '{RESOURCE_ID}' in zone '{ZONE}'...")
    start_time = time.time()
    
    while True:
        state = get_state()
        if not state:
            print("Could not retrieve state. Retrying in 15 seconds...")
            await asyncio.sleep(15)
            continue
            
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s elapsed] Current State: {state}")
        
        if state == "ACTIVE":
            print("🎉 TPU Queued Resource is now ACTIVE!")
            break
        elif state in ["FAILED", "SUSPENDING", "SUSPENDED"]:
            print(f"❌ TPU Queued Resource entered terminal state: {state}")
            sys.exit(1)
            
        await asyncio.sleep(15)
        
    print("Retrieving TPU VM external IP address...")
    # Give a tiny buffer for the VM creation details to fully register
    await asyncio.sleep(5)
    ip = get_node_ip()
    if ip:
        print(f"✅ TPU VM Node is up at IP: {ip}")
        print(f"🚀 vLLM should start serving on: http://{ip}:8000")
    else:
        print("⚠️ TPU VM is ACTIVE but could not retrieve network endpoint IP yet. Check 'gcloud compute tpus tpu-vm list'.")

if __name__ == "__main__":
    asyncio.run(monitor())
