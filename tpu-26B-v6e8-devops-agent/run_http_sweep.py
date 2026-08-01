#!/usr/bin/env python3
import asyncio
import statistics
import time

import httpx

URL = "http://34.176.80.135:8000/v1/chat/completions"
MODEL = "google/gemma-4-31B-it"

concurrencies = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
contexts = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]

results_file = "grid_benchmark_results.csv"

# Write header
with open(results_file, "w") as f:
    f.write("concurrency,context_len,throughput_req_sec,avg_latency_s,status\n")


async def test_config(c, ctx):
    # Skip configurations that exceed max capacity limits (789,760 tokens)
    if c * ctx > 789760:
        print(f"⏭️ Skipping concurrency={c}, context={ctx} (Exceeds max KV cache limit)")
        with open(results_file, "a") as f:
            f.write(f"{c},{ctx},0.0,0.0,skipped_capacity_limit\n")
        return

    print(f"🏃 Concurrency: {c:4d} | Context Window: {ctx:5d} tokens ... ", end="", flush=True)

    # We send max(c, 5) requests to get a representative average
    num_requests = max(c, 5)
    # Capped at 20 requests for high concurrency to keep it fast
    if c > 20:
        num_requests = min(c, 40)

    prompt = "hello " * ctx

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 10,  # short generation length to benchmark prefill/first-token throughput mainly
        "temperature": 0.0,
    }

    sem = asyncio.Semaphore(c)
    latencies = []

    async def send_req(client):
        async with sem:
            start = time.perf_counter()
            try:
                # 30 second timeout per request
                res = await client.post(URL, json=payload, timeout=30.0)
                if res.status_code == 200:
                    latencies.append(time.perf_counter() - start)
            except Exception:
                pass

    start_time = time.perf_counter()
    async with httpx.AsyncClient() as client:
        tasks = [send_req(client) for _ in range(num_requests)]
        await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_time

    successes = len(latencies)
    if successes > 0:
        throughput = successes / total_time
        avg_latency = statistics.mean(latencies)
        print(f"✅ Success | {throughput:6.2f} req/s | Latency: {avg_latency:6.3f}s (Took {total_time:.1f}s)")
        with open(results_file, "a") as f:
            f.write(f"{c},{ctx},{throughput:.3f},{avg_latency:.3f},success\n")
    else:
        print("❌ Failed (All requests timed out or failed)")
        with open(results_file, "a") as f:
            f.write(f"{c},{ctx},0.0,0.0,failed\n")


async def main():
    print(f"🚀 Starting HTTP-based grid benchmark sweep. Results will be saved to: {results_file}")
    for c in concurrencies:
        for ctx in contexts:
            await test_config(c, ctx)
    print("\n🏁 Sweep completed!")


if __name__ == "__main__":
    asyncio.run(main())
