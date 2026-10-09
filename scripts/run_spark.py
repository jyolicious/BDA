"""CLI script to execute Apache Spark analytics, aggregation, and MLlib clustering."""
import argparse
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.logger import get_logger
from src.common.utils import get_project_root, load_config
from src.spark.spark_session import get_spark_session, stop_spark_session
from src.spark.preprocessing import load_network_events
from src.spark.aggregation import aggregate_by_source_ip
from src.spark.feature_engineering import build_feature_pipeline
from src.spark.clustering import run_kmeans_clustering, save_spark_results

logger = get_logger("spark_cli")


def parse_args():
    parser = argparse.ArgumentParser(description="Execute Apache Spark Analytics & MLlib Clustering.")
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Input CSV dataset path or HDFS URI."
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="results/spark",
        help="Directory to store Spark analytical outputs."
    )
    parser.add_argument(
        "--k",
        type=int,
        default=4,
        help="Number of clusters for K-Means behavioral segmentation."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = get_project_root()
    start_total = time.time()

    if args.input:
        input_path = (root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    else:
        # Check HDFS staged file first, then local generated
        emulated_staged = root / "data" / "hdfs_emulated" / "cyber-threat" / "raw" / "events_10000.csv"
        generated_local = root / "data" / "generated" / "events_10000.csv"
        sample_local = root / "data" / "samples" / "sample_events.csv"

        if emulated_staged.exists():
            input_path = emulated_staged
        elif generated_local.exists():
            input_path = generated_local
        elif sample_local.exists():
            input_path = sample_local
        else:
            logger.error("No input dataset found. Run scripts/generate_data.py first.")
            sys.exit(1)

    output_dir = (root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)

    print("\n=======================================================")
    print("      APACHE SPARK DISTRIBUTED ANALYTICS & MLlib       ")
    print("=======================================================")
    print(f"Input Dataset:      {input_path}")
    print(f"Output Directory:   {output_dir}")
    print(f"Clusters (k):       {args.k}\n")

    spark = get_spark_session()
    try:
        # 1. Ingestion
        t0 = time.time()
        df = load_network_events(spark, input_path)
        t_ingest = time.time() - t0

        # 2. Aggregation
        t0 = time.time()
        agg_df = aggregate_by_source_ip(df)
        t_agg = time.time() - t0

        # 3. Feature Engineering
        t0 = time.time()
        scaled_df, scaler_model = build_feature_pipeline(agg_df)
        t_feat = time.time() - t0

        # 4. K-Means Clustering & Behavioral Interpretation
        t0 = time.time()
        clustered_df, kmeans_model, summary_pdf, profile_map = run_kmeans_clustering(
            scaled_df, k=args.k, seed=42
        )
        t_cluster = time.time() - t0

        # 5. Save Results
        save_spark_results(clustered_df, summary_pdf, output_dir)

        total_elapsed = time.time() - start_total

        print("\n--- SPARK PIPELINE EXECUTION SUMMARY ---")
        print(f"Data Ingestion:          {t_ingest:.3f}s")
        print(f"Distributed Aggregation: {t_agg:.3f}s")
        print(f"Feature Engineering:     {t_feat:.3f}s")
        print(f"MLlib K-Means:           {t_cluster:.3f}s")
        print(f"Total Spark Runtime:     {total_elapsed:.3f}s")
        print("----------------------------------------\n")

        print("--- CLUSTER BEHAVIORAL PROFILE SUMMARY ---")
        for idx, row in summary_pdf.iterrows():
            cid = int(row['cluster'])
            hosts = int(row['host_count'])
            prof = row['assigned_profile']
            sev = row['threat_severity']
            print(f"Cluster {cid} [{sev:<8}]: {hosts:<4} hosts -> {prof}")
            print(f"   Avg Bytes Sent: {row['mean_bytes_sent']:>10.1f} | Avg Ports: {row['mean_unique_ports']:>5.1f} | Failed Conns: {row['mean_failed_conns']:>5.1f}")
        print("-------------------------------------------\n")

    finally:
        stop_spark_session(spark)


if __name__ == "__main__":
    main()
