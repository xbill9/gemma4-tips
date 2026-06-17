import argparse
import asyncio
import csv
import os
import statistics
import time

import httpx

# Pre-defined grid
CONCURRENCIES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
CONTEXT_LENS = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16000]


async def send_request(client, url, model, prompt, max_tokens, semaphore):
    async with semaphore:
        payload = {"model": model, "prompt": prompt, "max_tokens": max_tokens, "temperature": 0.0, "stream": False}
        start = time.perf_counter()
        try:
            # We set a high timeout for large contexts and high concurrency
            response = await client.post(url, json=payload, timeout=180.0)
            latency = time.perf_counter() - start
            if response.status_code == 200:
                return {"success": True, "latency": latency}
            else:
                return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def run_combination(url, model, concurrency, context_len):
    # Construct a dummy prompt matching the context length
    # In SentencePiece/Gemma, repeating "a " gives a very reliable token count
    prompt = "a " * context_len
    max_tokens = 16  # Short generation to focus on context ingestion throughput

    # We run max(concurrency, 5) total requests to get a representative average
    num_requests = max(concurrency, 5)
    # Limit maximum total requests per sweep to prevent taking too long
    if num_requests > 100:
        num_requests = 100

    print(f"📊 Testing: Concurrency={concurrency}, Context={context_len}, Requests={num_requests}...")

    # We use a large connection limit to prevent client bottleneck
    limits = httpx.Limits(max_keepalive_connections=concurrency, max_connections=concurrency * 2)
    async with httpx.AsyncClient(limits=limits) as client:
        semaphore = asyncio.Semaphore(concurrency)
        start_batch = time.perf_counter()
        tasks = [send_request(client, url, model, prompt, max_tokens, semaphore) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_batch

        successes = [r for r in results if r["success"]]
        failures = [r for r in results if not r["success"]]
        latencies = [r["latency"] for r in successes]

        success_rate = len(successes) / num_requests
        errors = len(failures)

        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
            throughput = len(successes) / total_time
        else:
            avg_latency = 0.0
            p95_latency = 0.0
            throughput = 0.0

        print(
            f"   Results: Success={success_rate * 100:.1f}% | Throughput={throughput:.2f} req/s | Avg Lat={avg_latency:.2f}s | P95 Lat={p95_latency:.2f}s"
        )
        return {
            "concurrency": concurrency,
            "context_len": context_len,
            "success_rate": success_rate,
            "throughput": throughput,
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "errors": errors,
        }


async def main():
    parser = argparse.ArgumentParser(description="vLLM Grid Benchmark Sweep")
    parser.add_argument("--url", type=str, default="http://localhost:8000/v1/completions")
    parser.add_argument("--model", type=str, default="google/gemma-4-12B-it")
    parser.add_argument("--output", type=str, default="grid_benchmark_results.csv")
    args = parser.parse_args()

    # Initialize CSV file with headers if it doesn't exist
    file_exists = os.path.exists(args.output)

    # We open in append mode to save progress incrementally
    with open(args.output, "a", newline="") as csvfile:
        fieldnames = [
            "concurrency",
            "context_len",
            "success_rate",
            "throughput",
            "avg_latency",
            "p95_latency",
            "errors",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        # Run the grid search
        for context_len in CONTEXT_LENS:
            for concurrency in CONCURRENCIES:
                res = await run_combination(args.url, args.model, concurrency, context_len)
                writer.writerow(res)
                csvfile.flush()


if __name__ == "__main__":
    asyncio.run(main())
