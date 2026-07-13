#!/usr/bin/env python3
import os
import subprocess
import time
import sys

concurrencies = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
contexts = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]

results_file = "grid_benchmark_results.csv"

# Write header if new file
if not os.path.exists(results_file):
    with open(results_file, "w") as f:
        f.write("concurrency,context_len,throughput_req_sec,avg_latency_s,status\n")

print(f"🚀 Starting high-speed local grid benchmark sweep. Saving to: {results_file}")

for c in concurrencies:
    for ctx in contexts:
        # Skip configurations that exceed max capacity limits (to avoid stalling or capacity blocks)
        if c * ctx > 2195133:
            print(f"⏭️ Skipping concurrency={c}, context={ctx} (Exceeds max KV cache limit)")
            with open(results_file, "a") as f:
                f.write(f"{c},{ctx},0.0,0.0,skipped_capacity_limit\n")
            continue

        print(f"🏃 Concurrency: {c:4d} | Context Window: {ctx:5d} tokens ... ", end="", flush=True)
        num_prompts = max(c, 10)
        if c > 256:
            num_prompts = c

        # Local command inside container executed on the host
        cmd = [
            "sudo", "docker", "exec", "vllm-gemma4", "vllm", "bench", "serve",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--model", "google/gemma-4-31B-it",
            "--dataset-name", "random",
            "--num-prompts", str(num_prompts),
            "--random-input-len", str(ctx),
            "--random-output-len", "10",
            "--max-concurrency", str(c)
        ]

        start_run = time.time()
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            elapsed = time.time() - start_run

            if res.returncode == 0:
                output = res.stdout
                throughput = 0.0
                avg_latency = 0.0
                mean_ttft = 0.0
                mean_tpot = 0.0
                has_avg_latency_line = False

                for line in output.splitlines():
                    if "Request throughput (req/s):" in line:
                        try:
                            throughput = float(line.split(":")[1].strip())
                        except Exception:
                            pass
                    if "Average latency (s):" in line or "Average request latency (s):" in line:
                        try:
                            avg_latency = float(line.split(":")[1].strip())
                            has_avg_latency_line = True
                        except Exception:
                            pass
                    if "Mean TTFT (ms):" in line:
                        try:
                            mean_ttft = float(line.split(":")[1].strip())
                        except Exception:
                            pass
                    if "Mean TPOT (ms):" in line:
                        try:
                            mean_tpot = float(line.split(":")[1].strip())
                        except Exception:
                            pass

                if not has_avg_latency_line and (mean_ttft > 0 or mean_tpot > 0):
                    avg_latency = (mean_ttft + 9 * mean_tpot) / 1000.0

                print(f"✅ Success | {throughput:6.2f} req/s | Latency: {avg_latency:6.3f}s (Took {elapsed:.1f}s)")
                with open(results_file, "a") as f:
                    f.write(f"{c},{ctx},{throughput:.3f},{avg_latency:.3f},success\n")
            else:
                err_msg = res.stderr.strip().replace("\n", " ")[:100]
                print(f"❌ Failed (Code: {res.returncode}) | {err_msg}")
                with open(results_file, "a") as f:
                    f.write(f"{c},{ctx},0.0,0.0,failed_{res.returncode}\n")
        except subprocess.TimeoutExpired:
            print("⏳ Timeout")
            with open(results_file, "a") as f:
                f.write(f"{c},{ctx},0.0,0.0,timeout\n")
        except Exception as e:
            print(f"💥 Error: {e}")
            with open(results_file, "a") as f:
                f.write(f"{c},{ctx},0.0,0.0,error_{type(e).__name__}\n")

print("\n🏁 Sweep completed!")
