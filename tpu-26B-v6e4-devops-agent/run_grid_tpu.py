#!/usr/bin/env python3
import os
import subprocess
import time

def main():
    concurrencies = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    contexts = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16380]

    results_file = "/tmp/grid_benchmark_results.csv"

    # Write header if new file
    if not os.path.exists(results_file):
        with open(results_file, "w") as f:
            f.write("concurrency,context_len,throughput_req_sec,mean_ttft_ms,mean_itl_ms,status\n")

    print(f"Starting grid benchmark sweep on TPU node. Output: {results_file}")

    for c in concurrencies:
        for ctx in contexts:
            # Skip capacity limits (Max KV cache size: 458,240 tokens)
            if c * ctx > 458240:
                print(f"Skipping concurrency={c}, context={ctx} (Exceeds max KV cache limit of 458,240 tokens)")
                with open(results_file, "a") as f:
                    f.write(f"{c},{ctx},0.0,0.0,0.0,skipped_capacity_limit\n")
                continue

            print(f"Running concurrency={c:4d}, context={ctx:5d} tokens... ", end="", flush=True)
            num_prompts = max(c, 10)
            if c > 256:
                num_prompts = c

            cmd = (
                f"sudo docker run --rm --net=host vllm/vllm-tpu:nightly vllm bench serve "
                f"--host localhost "
                f"--port 8000 "
                f"--model hugg1ngfac3/gemma-4-26B-A4B-it-FP8 "
                f"--dataset-name random "
                f"--num-prompts {num_prompts} "
                f"--random-input-len {ctx} "
                f"--random-output-len 10 "
                f"--max-concurrency {c}"
            )

            start = time.time()
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
                elapsed = time.time() - start
                if res.returncode == 0:
                    output = res.stdout
                    throughput = 0.0
                    mean_ttft = 0.0
                    mean_itl = 0.0
                    for line in output.splitlines():
                        if "Request throughput (req/s):" in line:
                            throughput = float(line.split(":")[1].strip())
                        if "Mean TTFT (ms):" in line:
                            mean_ttft = float(line.split(":")[1].strip())
                        if "Mean ITL (ms):" in line:
                            mean_itl = float(line.split(":")[1].strip())
                    print(f"Success | {throughput:6.2f} req/s | TTFT: {mean_ttft:5.1f}ms | ITL: {mean_itl:5.1f}ms (Took {elapsed:.1f}s)")
                    with open(results_file, "a") as f:
                        f.write(f"{c},{ctx},{throughput:.3f},{mean_ttft:.1f},{mean_itl:.1f},success\n")
                else:
                    err = res.stderr.strip().replace("\n", " ")[:60]
                    print(f"Failed (Code {res.returncode}) | {err}")
                    with open(results_file, "a") as f:
                        f.write(f"{c},{ctx},0.0,0.0,0.0,failed_{res.returncode}\n")
            except subprocess.TimeoutExpired:
                print("Timeout")
                with open(results_file, "a") as f:
                    f.write(f"{c},{ctx},0.0,0.0,0.0,timeout\n")
            except Exception as e:
                print(f"Error: {e}")
                with open(results_file, "a") as f:
                    f.write(f"{c},{ctx},0.0,0.0,0.0,error_{type(e).__name__}\n")

    print("Sweep completed successfully!")

if __name__ == "__main__":
    main()
