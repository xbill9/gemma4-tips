#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

paths = {
    "2B": "../tpu-2B-v6e4-devops-agent/grid_benchmark_results.csv",
    "4B": "../tpu-4B-v6e4-devops-agent/grid_benchmark_results.csv",
    "12B": "../tpu-12B-v6e4-devops-agent/grid_benchmark_results.csv",
    "26B": "../tpu-26B-v6e4-devops-agent/grid_benchmark_results.csv",
    "31B": "grid_benchmark_results.csv"
}

all_data = []

for model, path in paths.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "throughput_req_sec" in df.columns:
            df = df.rename(columns={"throughput_req_sec": "throughput"})
        elif "throughput" not in df.columns and "req_per_sec" in df.columns:
            df = df.rename(columns={"req_per_sec": "throughput"})
        
        if "status" in df.columns:
            df = df[df["status"] == "success"].copy()
            
        df["model"] = model
        all_data.append(df)

df_all = pd.concat(all_data, ignore_index=True)

# Let's plot comparison at Context Length = 128 and 1024
target_contexts = [128, 1024]
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for i, ctx in enumerate(target_contexts):
    ax = axes[i]
    subset = df_all[df_all["context_len"] == ctx]
    
    sns.lineplot(data=subset, x="concurrency", y="throughput", hue="model", marker="o", ax=ax)
    ax.set_title(f"Throughput Comparison (Context Length: {ctx} tokens)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Concurrency (Users)", fontsize=10)
    ax.set_ylabel("Throughput (req/s)", fontsize=10)
    ax.set_xscale("log", base=2)
    ax.grid(True, which="both", ls="--", alpha=0.5)

plt.suptitle("Gemma 4 TPU v6e-4 Serving Performance Comparison by Model Size", fontsize=15, fontweight="bold")
plt.tight_layout()

artifact_dir = "/home/xbill/.gemini/antigravity-cli/brain/7fa7b26c-28fa-4083-a5aa-77f6a845b5ee"
plot_path = os.path.join(artifact_dir, "tpu_model_comparison.png")
plt.savefig(plot_path, dpi=300)
print(f"💾 Comparison plot saved to: {plot_path}")
print("Updating markdown report to embed the comparison plot...")

report_path = os.path.join(artifact_dir, "tpu_model_comparison.md")
if os.path.exists(report_path):
    with open(report_path, "r") as f:
        content = f.read()
    
    if "tpu_model_comparison.png" not in content:
        content = content.replace("## 📈 Throughput Comparison Table", "## 📊 Throughput Comparison Chart\n\n" + f"![Model Comparison Plot]({plot_path})\n\n## 📈 Throughput Comparison Table")
        with open(report_path, "w") as f:
            f.write(content)
        print("Updated markdown report.")
