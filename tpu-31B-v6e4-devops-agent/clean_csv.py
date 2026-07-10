#!/usr/bin/env python3
import os

csv_file = "grid_benchmark_results.csv"
if not os.path.exists(csv_file):
    print("Error: grid_benchmark_results.csv not found.")
    exit(1)

with open(csv_file, "r") as f:
    lines = f.read().splitlines()

# We know our new run starts at line index 289 (1-indexed line 290)
# Let's verify and grab all lines from line 290 onwards
new_run_lines = []
for line in lines[289:]:
    if line.strip():
        new_run_lines.append(line.strip())

header = "concurrency,context_len,throughput_req_sec,avg_latency_s,status"

# Rewrite the CSV with the correct header and our clean run data
with open(csv_file, "w") as f:
    f.write(header + "\n")
    for line in new_run_lines:
        f.write(line + "\n")

print(f"✅ Successfully cleaned {len(new_run_lines)} lines and wrote to {csv_file}")
