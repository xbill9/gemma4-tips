import os
from collections import defaultdict

def generate_markdown_report():
    csv_path = "grid_benchmark_results.csv"
    if not os.path.exists(csv_path):
        print("CSV results file not found!")
        return

    # Dictionary: (concurrency, context_len) -> throughput
    throughput_data = {}
    
    concurrencies = set()
    context_lens = set()

    with open(csv_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 5:
                if parts[0] == "concurrency":
                    continue
                try:
                    c = int(parts[0])
                    ctx = int(parts[1])
                    thr = float(parts[2])
                    status = parts[4].strip()
                    
                    if status == "success":
                        throughput_data[(c, ctx)] = thr
                        concurrencies.add(c)
                        context_lens.add(ctx)
                except ValueError:
                    pass

    sorted_concurrencies = sorted(list(concurrencies))
    sorted_context_lens = sorted(list(context_lens))

    # Build Throughput Markdown Table
    headers = ["Concurrency / Context"] + [f"{ctx}" for ctx in sorted_context_lens]
    sep_str = "|" + "|".join([" :---: "] * len(headers)) + "|"
    
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append(sep_str)
    
    for c in sorted_concurrencies:
        row_cells = [f"**{c}**"]
        for ctx in sorted_context_lens:
            val = throughput_data.get((c, ctx), None)
            if val is not None:
                row_cells.append(f"{val:.2f}")
            else:
                row_cells.append("-")
        lines.append("| " + " | ".join(row_cells) + " |")

    report = []
    report.append("# 📈 Gemma 4 4B TPU Benchmarking Sweep Report\n")
    report.append("This report contains the real measured throughput metrics (requests/second) for Gemma 4 (4B) deployed on GCP TPU v6e-1.\n")
    
    report.append("## 📊 Throughput (req/s)\n")
    report.append("\n".join(lines))
    report.append("\n\n*Note: High-concurrency and high-context configurations that exceeded the TPU VM's physical KV cache limit (~789,760 tokens) were automatically skipped to avoid Out-Of-Memory (OOM) errors.*")
    
    report_file = "benchmark_tables.md"
    with open(report_file, 'w') as f:
        f.write("\n".join(report))
        
    print(f"Successfully generated {report_file}")

if __name__ == "__main__":
    generate_markdown_report()
