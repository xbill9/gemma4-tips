#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def to_markdown_custom(df):
    header = "| concurrency | " + " | ".join(f"{c}" for c in df.columns) + " |"
    separator = "| --- | " + " | ".join("---" for _ in df.columns) + " |"
    rows = []
    for idx, row in df.iterrows():
        row_str = f"| **{idx}** | " + " | ".join(f"{val:.2f}" if isinstance(val, (int, float)) and not pd.isna(val) else "N/A" for val in row) + " |"
        rows.append(row_str)
    return "\n".join([header, separator] + rows)

def main():
    csv_path = "grid_benchmark_results.csv"
    if not os.path.exists(csv_path):
        print("CSV results file not found!")
        return

    data = []
    with open(csv_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if not parts or parts[0] == "concurrency":
                continue
            try:
                if len(parts) == 7:
                    # 7-column format: concurrency,context_len,success_rate,throughput,avg_latency,p95_latency,errors
                    data.append({
                        "concurrency": int(parts[0]),
                        "context_len": int(parts[1]),
                        "throughput": float(parts[3]),
                        "avg_latency": float(parts[4]),
                        "status": "success" if float(parts[2]) > 0.0 else "failed"
                    })
                elif len(parts) == 5:
                    # 5-column format: concurrency,context_len,throughput_req_sec,avg_latency_s,status
                    data.append({
                        "concurrency": int(parts[0]),
                        "context_len": int(parts[1]),
                        "throughput": float(parts[2]),
                        "avg_latency": float(parts[3]),
                        "status": parts[4]
                    })
            except ValueError:
                pass

    df = pd.DataFrame(data)
    df_success = df[df["status"] == "success"].copy()
    if df_success.empty:
        print("No successful points to plot!")
        return

    # Sort by avg_latency ascending so that non-zero latencies are kept by drop_duplicates
    df_success = df_success.sort_values(by="avg_latency", ascending=True)
    df_success = df_success.drop_duplicates(subset=["concurrency", "context_len"], keep="last")

    artifact_dir = "/home/xbill/.gemini/antigravity-cli/brain/620a9b2c-4980-4300-8334-7287f65257ba"
    os.makedirs(artifact_dir, exist_ok=True)

    sns.set_theme(style="whitegrid")

    # 1. Throughput Heatmap
    plt.figure(figsize=(14, 10))
    pivot_throughput = df_success.pivot(index="concurrency", columns="context_len", values="throughput")
    pivot_throughput = pivot_throughput.sort_index(ascending=False).sort_index(axis=1)

    sns.heatmap(pivot_throughput, annot=True, fmt=".2f", cmap="viridis", cbar_kws={"label": "Throughput (req/s)"})
    plt.title(
        "Gemma 4 26B Serving Throughput (req/s)\nConcurrency vs Context Window",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    plt.ylabel("Concurrency (Users)", fontsize=12)
    plt.xlabel("Context Window (Tokens)", fontsize=12)
    plt.tight_layout()
    plt.savefig("throughput_heatmap.png", dpi=300)
    plt.savefig(os.path.join(artifact_dir, "throughput_heatmap.png"), dpi=300)
    plt.close()
    print("Saved: throughput_heatmap.png")

    # 2. Latency Heatmap
    plt.figure(figsize=(14, 10))
    pivot_latency = df_success.pivot(index="concurrency", columns="context_len", values="avg_latency")
    pivot_latency = pivot_latency.sort_index(ascending=False).sort_index(axis=1)

    sns.heatmap(pivot_latency, annot=True, fmt=".3f", cmap="magma", cbar_kws={"label": "Avg Latency (s)"})
    plt.title(
        "Gemma 4 26B Average Latency (s)\nConcurrency vs Context Window",
        fontsize=16,
        fontweight="bold",
        pad=20
    )
    plt.ylabel("Concurrency (Users)", fontsize=12)
    plt.xlabel("Context Window (Tokens)", fontsize=12)
    plt.tight_layout()
    plt.savefig("latency_heatmap.png", dpi=300)
    plt.savefig(os.path.join(artifact_dir, "latency_heatmap.png"), dpi=300)
    plt.close()
    print("Saved: latency_heatmap.png")

    # 3. Generate Markdown Report Tables
    report = []
    report.append("# 📈 Gemma 4 TPU Benchmarking Sweep Report\n")
    report.append("## 📊 Throughput (req/s) Table\n")
    report.append(to_markdown_custom(pivot_throughput.sort_index(ascending=True)))
    report.append("\n\n## ⏱️ Average Request Latency (s) Table\n")
    report.append(to_markdown_custom(pivot_latency.sort_index(ascending=True)))

    report_file = os.path.join(artifact_dir, "benchmark_tables.md")
    with open(report_file, "w") as f:
        f.write("\n".join(report))
    print(f"Saved Markdown report to: {report_file}")

if __name__ == "__main__":
    main()
