import asyncio
import sys
import os

# Ensure the parent directory is in the python path so we can import server
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server import manage_queued_resource

async def main():
    print("Initiating redeployment of vLLM with google/gemma-4-26B-it using existing reservation...")
    result = await manage_queued_resource(
        resource_id="vllm-gemma4-qr",
        reserved=False,
        model_name="google/gemma-4-26B-it"
    )
    print("\nResult:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
