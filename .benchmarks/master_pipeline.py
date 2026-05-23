#!/usr/bin/env python3
"""
Master Pipeline: Benchmark + Sensitivity Analysis + Visualization
Run this single script to generate all data and figures for your paper.
"""

import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import time
from pathlib import Path
from typing import List, Dict
import httpx
import logging

# Import or paste the BenchmarkConfig, QueryGenerator, and BenchmarkRunner classes here
# For brevity, assuming you have benchmark_10k.py in the same directory.
# If not, paste the classes from the previous responses here.
from benchmark_10k import BenchmarkConfig, QueryGenerator, BenchmarkRunner, QueryResult

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalysisPipeline:
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results_dir = config.output_dir
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        
    async def run_benchmark(self):
        logger.info("="*60)
        logger.info("PHASE 1: RUNNING 10K BENCHMARK")
        logger.info("="*60)
        
        generator = QueryGenerator(seed=42)
        test_queries = generator.generate_all(self.config)
        
        async with BenchmarkRunner(self.config) as runner:
            await runner.run_benchmark(test_queries)
            runner.save_results(self.results_dir)
        
        logger.info("✅ Benchmark complete. Results saved.")
        return runner.metrics

    def run_sensitivity_analysis(self):
        logger.info("="*60)
        logger.info("PHASE 2: THRESHOLD SENSITIVITY ANALYSIS")
        logger.info("="*60)
        
        csv_path = os.path.join(self.results_dir, "raw_results.csv")
        if not os.path.exists(csv_path):
            logger.error("raw_results.csv not found. Run benchmark first.")
            return

        df = pd.read_csv(csv_path)
        
        # Simulate sensitivity by checking similarity scores against thresholds
        # This avoids re-querying the API
        thresholds = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99]
        sensitivity_data = []
        
        logger.info(f"Analyzing {len(df)} results across {len(thresholds)} thresholds...")
        
        for thresh in thresholds:
            # If similarity >= threshold, it counts as a hit
            # We assume the API returns similarity even for misses (common in semantic search APIs)
            hits = df[df['similarity'] >= thresh]
            hit_rate = (len(hits) / len(df)) * 100
            avg_prec = hits['similarity'].mean() if len(hits) > 0 else 0
            avg_lat = hits['latency_ms'].mean() if len(hits) > 0 else 0
            
            sensitivity_data.append({
                'threshold': thresh,
                'hit_rate_pct': hit_rate,
                'avg_precision': avg_prec,
                'avg_latency_ms': avg_lat
            })
            
        sens_df = pd.DataFrame(sensitivity_data)
        
        # Plot Sensitivity
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=sens_df, x='threshold', y='hit_rate_pct', marker='o', label='Hit Rate (%)', color='#2196F3')
        sns.lineplot(data=sens_df, x='threshold', y='avg_precision', marker='s', label='Avg Precision', color='#4CAF50')
        plt.title('Threshold Sensitivity: Hit Rate vs Precision')
        plt.xlabel('Similarity Threshold')
        plt.ylabel('Score / Percentage')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        path = os.path.join(self.results_dir, "fig_threshold_sensitivity.png")
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ Sensitivity analysis saved to {path}")

    def generate_plots(self):
        logger.info("="*60)
        logger.info("PHASE 3: GENERATING PAPER FIGURES")
        logger.info("="*60)
        
        csv_path = os.path.join(self.results_dir, "raw_results.csv")
        df = pd.read_csv(csv_path)
        
        # 1. Hit Rate by Domain
        domain_stats = df.groupby('domain')['is_hit'].mean() * 100
        plt.figure(figsize=(8, 5))
        sns.barplot(x=domain_stats.index, y=domain_stats.values, color='#2196F3')
        plt.title('Cache Hit Rate by Domain')
        plt.ylabel('Hit Rate (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "fig_domain_hitrate.png"), dpi=300)
        plt.close()
        
        # 2. Latency CDF
        plt.figure(figsize=(8, 5))
        sns.ecdfplot(data=df[df['is_hit']==True], x='latency_ms', label='Hit')
        sns.ecdfplot(data=df[df['is_hit']==False], x='latency_ms', label='Miss')
        plt.title('Latency CDF: Hit vs Miss')
        plt.xlabel('Latency (ms)')
        plt.ylabel('CDF')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "fig_latency_cdf.png"), dpi=300)
        plt.close()
        
        logger.info("✅ All figures generated successfully.")

async def main():
    config = BenchmarkConfig()
    pipeline = AnalysisPipeline(config)
    
    # Phase 1: Benchmark
    await pipeline.run_benchmark()
    
    # Phase 2: Sensitivity (Offline analysis from CSV)
    pipeline.run_sensitivity_analysis()
    
    # Phase 3: Plots
    pipeline.generate_plots()
    
    print("\n🎉 Pipeline Complete! Check the 'benchmark_results/' folder.")

if __name__ == "__main__":
    asyncio.run(main())