#!/usr/bin/env python3
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

paths = {
    # v6e-4 (4 chips)
    "2B (v6e-4)": "../tpu-2B-v6e4-devops-agent/grid_benchmark_results.csv",
    "4B (v6e-4)": "../tpu-4B-v6e4-devops-agent/grid_benchmark_results.csv",
    "12B (v6e-4)": "../tpu-12B-v6e4-devops-agent/grid_benchmark_results.csv",
    "26B (v6e-4)": "../tpu-26B-v6e4-devops-agent/grid_benchmark_results.csv",
    "31B (v6e-8)": "grid_benchmark_results.csv",
    # v6e-1 (1 chip)
    "2B (v6e-1)": "../tpu-2B-v6e1-devops-agent/grid_benchmark_results.csv",
    "4B (v6e-1)": "../tpu-4B-v6e1-devops-agent/grid_benchmark_results.csv",
    "12B (v6e-1)": "../tpu-12B-v6e1-devops-agent/grid_benchmark_results.csv",
    "12B-MTP (v6e-1)": "../tpu-12B-mtp-v6e1-devops-agent/grid_benchmark_results.csv",
    "12B-Quant (v6e-1)": "../tpu-12B-quant-v6e1-devops-agent/grid_benchmark_results.csv",
}

all_data = []

for label, path in paths.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "throughput_req_sec" in df.columns:
            df = df.rename(columns={"throughput_req_sec": "throughput"})
        elif "throughput" not in df.columns and "req_per_sec" in df.columns:
            df = df.rename(columns={"req_per_sec": "throughput"})

        if "status" in df.columns:
            df = df[df["status"] == "success"].copy()

        df["model"] = label
        all_data.append(df)

df_all = pd.concat(all_data, ignore_index=True)

# Comparison points: Concurrencies: 1, 16, 64. Contexts: 128, 1024.
grid_points = [
    (1, 128),
    (1, 1024),
    (16, 128),
    (16, 1024),
    (64, 128),
    (64, 1024),
]

comp_rows = []
for c, ctx in grid_points:
    row: dict = {"Concurrency": c, "Context": ctx}
    for label in paths.keys():
        subset = df_all[(df_all["concurrency"] == c) & (df_all["context_len"] == ctx) & (df_all["model"] == label)]
        if not subset.empty:
            throughput = subset.iloc[0]["throughput"]
            status = subset.iloc[0].get("status", "success")
            if "skipped" in str(status) or throughput == 0.0:
                row[label] = "Skipped"
            else:
                row[label] = f"{throughput:.2f} req/s"
        else:
            row[label] = "N/A"
    comp_rows.append(row)

df_comp = pd.DataFrame(comp_rows)

# Simple Markdown builder
headers = ["Concurrency", "Context"] + list(paths.keys())
tbl_lines = []
tbl_lines.append("| " + " | ".join(headers) + " |")
tbl_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
for r in comp_rows:
    vals = [str(r["Concurrency"]), str(r["Context"])]
    for label in paths.keys():
        vals.append(str(r[label]))
    tbl_lines.append("| " + " | ".join(vals) + " |")
table_md = "\n".join(tbl_lines)

# Plotting
target_contexts = [128, 1024]
fig, axes = plt.subplots(1, 2, figsize=(18, 7))

for i, ctx in enumerate(target_contexts):
    ax = axes[i]
    subset = df_all[df_all["context_len"] == ctx]

    sns.lineplot(data=subset, x="concurrency", y="throughput", hue="model", marker="o", ax=ax)
    ax.set_title(f"Throughput Comparison (Context Length: {ctx} tokens)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Concurrency (Users)", fontsize=10)
    ax.set_ylabel("Throughput (req/s)", fontsize=10)
    ax.set_xscale("log", base=2)
    ax.grid(True, which="both", ls="--", alpha=0.5)

plt.suptitle("Gemma 4 serving performance: TPU v6e-4 (4 chips) vs TPU v6e-1 (1 chip)", fontsize=15, fontweight="bold")
plt.tight_layout()

artifact_dir = "/home/xbill/.gemini/antigravity-cli/brain/7fa7b26c-28fa-4083-a5aa-77f6a845b5ee"
plot_path = os.path.join(artifact_dir, "tpu_v6e4_vs_v6e1_comparison.png")
plt.savefig(plot_path, dpi=300)

report_path = os.path.join(artifact_dir, "tpu_model_comparison.md")

with open(report_path, "w") as f:
    f.write("# 📊 GCP TPU Gemma 4 Model Comparison: v6e-4 (4 chips) vs v6e-1 (1 chip)\n\n")
    f.write(
        "This report compares the request throughput (req/s) across different model configurations and hardware node sizes (4-chip v6e-4 vs 1-chip v6e-1).\n\n"
    )
    f.write("## 📊 Throughput Comparison Chart\n\n")
    f.write(f"![v6e4 vs v6e1 Comparison Plot]({plot_path})\n\n")
    f.write("## 📈 Throughput Comparison Table\n\n")
    f.write(table_md)
    f.write("\n\n## 🔍 SRE Analysis & Performance Observations\n")
    f.write(
        "1. **Node Size Scaling Advantage (v6e-4 vs v6e-1):** The 4-chip v6e-4 node provides a massive processing advantage compared to the single-chip v6e-1. For example, the 4B model at Concurrency 64 scales from `55.33 req/s` on v6e-1 to `88.11 req/s` on v6e-4.\n"
    )
    f.write(
        "2. **Large Model Servability:** Large models like 26B and 31B require the distributed memory and sharding topology of the 4-chip v6e-4 node (128GB HBM total) to run context sweeps efficiently without severe preemption or OOM errors.\n"
    )

print("Successfully updated comparison report.")
