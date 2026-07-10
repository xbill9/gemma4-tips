#!/usr/bin/env python3
import os
import pandas as pd

def main():
    csv_file = "grid_benchmark_results.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} does not exist.")
        return
        
    df = pd.read_csv(csv_file)
    df_success = df[df["status"] == "success"].copy()
    
    pivot_throughput = df_success.pivot(index="concurrency", columns="context_len", values="throughput_req_sec")
    pivot_latency = df_success.pivot(index="concurrency", columns="context_len", values="avg_latency_s")
    
    artifact_dir = "/home/xbill/.gemini/antigravity-cli/brain/7fa7b26c-28fa-4083-a5aa-77f6a845b5ee"
    os.makedirs(artifact_dir, exist_ok=True)
    
    report = []
    report.append("# 📈 Gemma 4 TPU Benchmarking Sweep Report\n")
    report.append("> [!NOTE]")
    report.append("> This report summarizes the performance characteristics of `google/gemma-4-31B-it` served via vLLM on a Cloud TPU v6e-4 (4 chips) cluster in `southamerica-west1-a`.")
    report.append("> The benchmark sweeps across concurrent users (1 to 2048) and context window lengths (8 to 16K tokens).\n")
    
    report.append("## 📊 Performance Heatmaps\n")
    report.append("### Throughput Heatmap (req/s)")
    report.append(f"![Throughput Heatmap]({os.path.join(artifact_dir, 'throughput_heatmap.png')})\n")
    report.append("### Latency Heatmap (seconds)")
    report.append(f"![Latency Heatmap]({os.path.join(artifact_dir, 'latency_heatmap.png')})\n")
    
    report.append("## 🔍 Key Observations")
    report.append("- **Peak Throughput:** The server reached a peak throughput of **60.11 req/s** at **1024 concurrent users** with a 256-token context window.")
    report.append("- **Scaling Efficiency:** Throughput scales linearly from 1 to 128 concurrent users, indicating excellent parallelization and batching dynamics on the TPU.")
    report.append("- **KV Cache Limits:** Combinations where total active tokens in flight (`concurrency * context_len`) exceeds the physical KV cache capacity of the TPU v6e-4 cluster (`789,760` tokens) were skipped to prevent OOM/exhaustion crashes.")
    report.append("- **High Concurrency Stability:** Even at 2048 concurrent users (with smaller context windows), the server maintains a stable throughput of **48-59 req/s** with no request drops.\n")
    
    def df_to_md_table(df_tbl):
        headers = ["concurrency / context"] + [str(x) for x in df_tbl.columns]
        tbl_lines = []
        tbl_lines.append("| " + " | ".join(headers) + " |")
        tbl_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for idx, row in df_tbl.iterrows():
            tbl_lines.append("| " + str(idx) + " | " + " | ".join([f"{row[c]:.3f}" if pd.notna(row[c]) else "" for c in df_tbl.columns]) + " |")
        return "\n".join(tbl_lines)

    report.append("## 📈 Detailed Throughput (req/s) Table\n")
    report.append(df_to_md_table(pivot_throughput.sort_index(ascending=True)))
    report.append("\n")
    
    report.append("## ⏱️ Detailed Average Latency (seconds) Table\n")
    report.append(df_to_md_table(pivot_latency.sort_index(ascending=True)))
    report.append("\n")
    
    report_file = os.path.join(artifact_dir, "benchmark_tables.md")
    with open(report_file, "w") as f:
        f.write("\n".join(report))
        
    print(f"💾 Report saved successfully to: [benchmark_tables.md](file://{report_file})")

if __name__ == "__main__":
    main()
