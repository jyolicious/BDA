"""Spark MLlib K-Means Clustering and Behavioral Profile Interpretation."""
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pandas as pd
from pyspark.ml.clustering import KMeans, KMeansModel
from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col, count, round, when, udf
from pyspark.sql.types import StringType
from src.common.logger import get_logger

logger = get_logger("spark_clustering")


def interpret_clusters(summary_df: pd.DataFrame) -> Dict[int, Dict[str, str]]:
    """Analyze cluster centroids and assign explainable cybersecurity profiles."""
    profile_map: Dict[int, Dict[str, str]] = {}

    for _, row in summary_df.iterrows():
        cid = int(row["cluster"])
        ev_count = row["mean_event_count"]
        bytes_sent = row["mean_bytes_sent"]
        ports = row["mean_unique_ports"]
        failed = row["mean_failed_conns"]
        packets = row["mean_packet_count"]

        # Behavioral heuristics based on domain properties
        if ports > 10.0 and failed > 10.0:
            profile = "Reconnaissance / Port Scanner"
            severity = "HIGH"
            rationale = f"Probing {ports:.1f} distinct ports with {failed:.1f} connection rejections."

        elif bytes_sent > 500000.0 and packets > 150.0:
            profile = "Volumetric Flood / DDoS Attack"
            severity = "CRITICAL"
            rationale = f"High traffic volume ({bytes_sent/1024:.1f} KB) and burst packet rate ({packets:.1f} pkts/flow)."

        elif bytes_sent > 100000.0:
            profile = "Covert Channel / Data Exfiltration"
            severity = "MEDIUM"
            rationale = f"Asymmetric data transmission volume exceeding baseline expectations."

        else:
            profile = "Normal Client Activity"
            severity = "LOW"
            rationale = "Flow volume, duration, and port distribution conform to standard usage."

        profile_map[cid] = {
            "profile": profile,
            "severity": severity,
            "rationale": rationale
        }

    return profile_map


def run_kmeans_clustering(
    scaled_df: DataFrame,
    k: int = 4,
    seed: int = 42,
    max_iter: int = 30
) -> Tuple[DataFrame, KMeansModel, pd.DataFrame, Dict[int, Dict[str, str]]]:
    """Train K-Means clustering and interpret resulting behavioral clusters."""
    logger.info(f"Training Spark MLlib KMeans model (k={k}, seed={seed}, max_iter={max_iter})...")

    kmeans = KMeans(k=k, seed=seed, maxIter=max_iter, featuresCol="features", predictionCol="cluster")
    model = kmeans.fit(scaled_df)
    clustered_df = model.transform(scaled_df)

    # Compute centroid profile summary per cluster
    logger.info("Computing cluster centroid metrics...")
    summary_spark = clustered_df.groupBy("cluster").agg(
        count("*").alias("host_count"),
        round(avg("event_count"), 2).alias("mean_event_count"),
        round(avg("total_bytes_sent"), 2).alias("mean_bytes_sent"),
        round(avg("total_bytes_received"), 2).alias("mean_bytes_recv"),
        round(avg("avg_packet_count"), 2).alias("mean_packet_count"),
        round(avg("unique_dest_ports"), 2).alias("mean_unique_ports"),
        round(avg("failed_conn_count"), 2).alias("mean_failed_conns"),
        round(avg("avg_duration_ms"), 2).alias("mean_duration_ms")
    ).orderBy("cluster")

    summary_pdf = summary_spark.toPandas()

    # Assign explainable behavioral interpretations
    profile_map = interpret_clusters(summary_pdf)
    summary_pdf["assigned_profile"] = summary_pdf["cluster"].map(lambda c: profile_map[c]["profile"])
    summary_pdf["threat_severity"] = summary_pdf["cluster"].map(lambda c: profile_map[c]["severity"])
    summary_pdf["detection_rationale"] = summary_pdf["cluster"].map(lambda c: profile_map[c]["rationale"])

    logger.info("Assigned interpretable cybersecurity profiles to all clusters:")
    for cid, info in profile_map.items():
        logger.info(f"  Cluster {cid}: {info['profile']} [{info['severity']}] - {info['rationale']}")

    # Attach profile labels to the Spark DataFrame
    profile_udf = udf(lambda c: profile_map.get(c, {}).get("profile", "Unknown"), StringType())
    severity_udf = udf(lambda c: profile_map.get(c, {}).get("severity", "LOW"), StringType())

    final_df = (
        clustered_df
        .withColumn("behavioral_profile", profile_udf(col("cluster")))
        .withColumn("threat_severity", severity_udf(col("cluster")))
    )

    return final_df, model, summary_pdf, profile_map


def save_spark_results(
    clustered_df: DataFrame,
    summary_pdf: pd.DataFrame,
    output_dir: Path
) -> None:
    """Save Spark features, cluster assignments, and summary reports to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save Cluster Summary
    summary_path = output_dir / "cluster_summary.csv"
    summary_pdf.to_csv(summary_path, index=False)
    logger.info(f"Saved cluster summary to: {summary_path}")

    # 2. Save IP Level Features & Cluster Assignments
    # Drop dense vector columns before saving to clean readable CSV
    cols_to_export = [
        "source_ip", "event_count", "total_bytes_sent", "total_bytes_received",
        "avg_packet_count", "unique_dest_ports", "failed_conn_count",
        "avg_duration_ms", "protocol_diversity", "cluster",
        "behavioral_profile", "threat_severity"
    ]
    export_df = clustered_df.select([col(c) for c in cols_to_export])
    pdf_clusters = export_df.toPandas()

    clusters_path = output_dir / "spark_clusters.csv"
    pdf_clusters.to_csv(clusters_path, index=False)
    logger.info(f"Saved IP cluster assignments to: {clusters_path}")

    # 3. Save IP Features
    features_path = output_dir / "spark_ip_features.csv"
    pdf_features = pdf_clusters.drop(columns=["cluster", "behavioral_profile", "threat_severity"])
    pdf_features.to_csv(features_path, index=False)
    logger.info(f"Saved IP features to: {features_path}")
