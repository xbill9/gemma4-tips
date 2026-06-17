import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load the benchmark results
df = pd.read_csv("grid_benchmark_results.csv")

# The CSV contains two sweeps. Let's take the second sweep (rows 144 to 287).
latest_df = df.iloc[-144:].copy()

# 1. Throughput Heatmap
pivot_thru = latest_df.pivot(index="context_len", columns="concurrency", values="throughput")
plt.figure(figsize=(10, 7))
im = plt.imshow(pivot_thru.values, cmap="YlGnBu", aspect="auto")
plt.colorbar(im, label="Throughput (req/s)")
plt.xticks(np.arange(len(pivot_thru.columns)), pivot_thru.columns)
plt.yticks(np.arange(len(pivot_thru.index)), pivot_thru.index)
plt.title("Throughput (req/s) by Context Length & Concurrency")
plt.xlabel("Concurrency (Users)")
plt.ylabel("Context Length (Tokens)")

# Annotate values
for i in range(len(pivot_thru.index)):
    for j in range(len(pivot_thru.columns)):
        val = pivot_thru.values[i, j]
        plt.text(
            j,
            i,
            f"{val:.1f}",
            ha="center",
            va="center",
            color="black" if val < pivot_thru.values.max() / 2 else "white",
        )

plt.tight_layout()
plt.savefig("throughput_heatmap.png", dpi=300)
plt.close()

# 2. Average Latency Heatmap
pivot_lat = latest_df.pivot(index="context_len", columns="concurrency", values="avg_latency")
plt.figure(figsize=(10, 7))
im = plt.imshow(pivot_lat.values, cmap="OrRd", aspect="auto")
plt.colorbar(im, label="Average Latency (s)")
plt.xticks(np.arange(len(pivot_lat.columns)), pivot_lat.columns)
plt.yticks(np.arange(len(pivot_lat.index)), pivot_lat.index)
plt.title("Average Latency (seconds) by Context Length & Concurrency")
plt.xlabel("Concurrency (Users)")
plt.ylabel("Context Length (Tokens)")

# Annotate values
for i in range(len(pivot_lat.index)):
    for j in range(len(pivot_lat.columns)):
        val = pivot_lat.values[i, j]
        plt.text(
            j, i, f"{val:.2f}", ha="center", va="center", color="black" if val < pivot_lat.values.max() / 2 else "white"
        )

plt.tight_layout()
plt.savefig("latency_heatmap.png", dpi=300)
plt.close()

# 3. Throughput Line Plot
plt.figure(figsize=(10, 6))
plot_df = latest_df[latest_df["context_len"] <= 4096]
for ctx in sorted(plot_df["context_len"].unique()):
    sub = plot_df[plot_df["context_len"] == ctx]
    plt.plot(sub["concurrency"], sub["throughput"], marker="o", label=f"{ctx} tokens")

plt.xscale("log", base=2)
plt.xticks(plot_df["concurrency"].unique(), plot_df["concurrency"].unique())
plt.title("Throughput vs Concurrency (Successful Context Lengths)")
plt.xlabel("Concurrency (log scale)")
plt.ylabel("Throughput (req/s)")
plt.legend(title="Context Length")
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("throughput_line.png", dpi=300)
plt.close()

print("Plots generated successfully: throughput_heatmap.png, latency_heatmap.png, throughput_line.png")

# Let's output markdown tables for our report
for ctx in sorted(latest_df["context_len"].unique()):
    sub = latest_df[latest_df["context_len"] == ctx]
    print(f"\n#### Context Length: {ctx} Tokens")
    print("| Concurrency | Success Rate | Throughput (req/s) | Avg Latency (s) | P95 Latency (s) |")
    print("|---|---|---|---|---|")
    for _, row in sub.iterrows():
        print(
            f"| {int(row['concurrency'])} | {row['success_rate'] * 100:.1f}% | {row['throughput']:.2f} | {row['avg_latency']:.3f} | {row['p95_latency']:.3f} |"
        )
