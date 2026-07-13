#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def main():
    tp4_file = "grid_benchmark_results_tp4_backup.csv"
    tp8_file = "grid_benchmark_results.csv"

    if not os.path.exists(tp4_file) or not os.path.exists(tp8_file):
        print("❌ Error: One or both benchmark files (TP4 baseline and TP8 upgraded) are missing.")
        return

    # Load data
    df_tp4 = pd.read_csv(tp4_file)
    df_tp4 = df_tp4[df_tp4["status"] == "success"].copy()
    df_tp4["Configuration"] = "TP=4 (Baseline)"

    df_tp8 = pd.read_csv(tp8_file)
    df_tp8 = df_tp8[df_tp8["status"] == "success"].copy()
    df_tp8["Configuration"] = "TP=8 (Upgraded)"

    # Combine dataframes
    df_all = pd.concat([df_tp4, df_tp8], ignore_index=True)

    # We want to compare across specific context lengths
    target_contexts = [128, 1024, 4096]

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 3, figsize=(22, 11))

    # Curated premium color palette
    palette = {"TP=4 (Baseline)": "#5c768d", "TP=8 (Upgraded)": "#f368e0"}

    for col_idx, ctx in enumerate(target_contexts):
        subset = df_all[df_all["context_len"] == ctx]

        # ----------------------------------------------------
        # Row 0: Throughput (req/s) vs Concurrency
        # ----------------------------------------------------
        ax_thru = axes[0, col_idx]
        sns.lineplot(
            data=subset, 
            x="concurrency", 
            y="throughput_req_sec", 
            hue="Configuration", 
            palette=palette,
            marker="o", 
            markersize=8, 
            linewidth=2.5,
            ax=ax_thru
        )
        ax_thru.set_title(f"Throughput | Context: {ctx} Tokens", fontsize=14, fontweight="bold", pad=12)
        ax_thru.set_xlabel("Concurrency (Users)", fontsize=11)
        ax_thru.set_ylabel("Throughput (req/s)", fontsize=11)
        ax_thru.set_xscale("log", base=2)
        ax_thru.grid(True, which="both", ls="--", alpha=0.6)
        
        # Only show legend on the middle plot to avoid clutter
        if col_idx != 1:
            ax_thru.get_legend().remove()
        else:
            ax_thru.legend(title="Configuration", fontsize=11, title_fontsize=11, loc="upper left")

        # ----------------------------------------------------
        # Row 1: Average Latency (s) vs Concurrency
        # ----------------------------------------------------
        ax_lat = axes[1, col_idx]
        sns.lineplot(
            data=subset, 
            x="concurrency", 
            y="avg_latency_s", 
            hue="Configuration", 
            palette=palette,
            marker="s", 
            markersize=8, 
            linewidth=2.5,
            ax=ax_lat
        )
        ax_lat.set_title(f"Request Latency | Context: {ctx} Tokens", fontsize=14, fontweight="bold", pad=12)
        ax_lat.set_xlabel("Concurrency (Users)", fontsize=11)
        ax_lat.set_ylabel("Average Latency (seconds)", fontsize=11)
        ax_lat.set_xscale("log", base=2)
        ax_lat.grid(True, which="both", ls="--", alpha=0.6)
        ax_lat.get_legend().remove()

    plt.suptitle("Gemma-4 31B Serving Optimization: TP=4 vs. TP=8 Telemetry Comparison\n(vLLM on GCP TPU v6e-8)", fontsize=18, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Save files locally and directly to current brain artifacts
    plot_name = "tp_comparison_chart.png"
    plt.savefig(plot_name, dpi=300)
    print(f"💾 Saved local comparison plot: {plot_name}")

    artifact_dir = "/home/xbill/.gemini/antigravity-cli/brain/93eebc37-dd44-479e-b313-1656d3fefe68"
    os.makedirs(artifact_dir, exist_ok=True)
    plt.savefig(os.path.join(artifact_dir, plot_name), dpi=300)
    print(f"💾 Saved artifact comparison plot to: {os.path.join(artifact_dir, plot_name)}")

if __name__ == "__main__":
    main()
