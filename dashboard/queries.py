"""Data query and abstraction layer for the Streamlit Cyber Intelligence Dashboard."""
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from src.common.utils import get_project_root
from src.database.mongodb import MongoDBManager


def get_db_instance() -> MongoDBManager:
    """Return an active MongoDBManager instance."""
    return MongoDBManager()


def fetch_recent_alerts(db: MongoDBManager, limit: int = 50) -> pd.DataFrame:
    """Query recent threat alerts from MongoDB or fallback buffer into a DataFrame."""
    raw_alerts = db.query_recent_alerts(limit=limit)
    if not raw_alerts:
        return pd.DataFrame(columns=[
            "timestamp", "source_ip", "threat_type", "threat_score",
            "severity", "event_count", "unique_ports", "detection_reason"
        ])
    df = pd.DataFrame(raw_alerts)
    # Ensure necessary columns exist
    for col in ["timestamp", "source_ip", "threat_type", "threat_score", "severity", "event_count", "unique_ports", "detection_reason"]:
        if col not in df.columns:
            df[col] = None
    return df


def fetch_top_suspicious_ips(db: MongoDBManager, limit: int = 10) -> pd.DataFrame:
    """Query ranked suspicious source IPs from MongoDB."""
    raw_ips = db.get_top_suspicious_ips(limit=limit)
    if not raw_ips:
        return pd.DataFrame(columns=["source_ip", "threat_score", "severity", "threat_types", "event_count", "last_seen"])
    df = pd.DataFrame(raw_ips)
    if "threat_types" in df.columns:
        df["threat_types"] = df["threat_types"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
    return df


def fetch_threat_distribution(db: MongoDBManager) -> pd.DataFrame:
    """Query threat classification distribution counts."""
    dist = db.get_threat_distribution()
    data = [{"threat_type": k, "count": v} for k, v in dist.items() if v > 0]
    if not data:
        data = [{"threat_type": "None", "count": 0}]
    return pd.DataFrame(data)


def load_mapreduce_results() -> Dict[str, pd.DataFrame]:
    """Load historical MapReduce outputs from results directory."""
    root = get_project_root()
    mr_dir = root / "results" / "mapreduce"
    res = {}

    top_ips_file = mr_dir / "mapreduce_top_ips.csv"
    if top_ips_file.exists():
        res["top_ips"] = pd.read_csv(top_ips_file)

    attacks_file = mr_dir / "mapreduce_attack_counts.csv"
    if attacks_file.exists():
        res["attack_counts"] = pd.read_csv(attacks_file)

    return res


def load_spark_results() -> Dict[str, pd.DataFrame]:
    """Load Spark aggregation and MLlib clustering results."""
    root = get_project_root()
    spark_dir = root / "results" / "spark"
    res = {}

    clusters_file = spark_dir / "cluster_summary.csv"
    if clusters_file.exists():
        res["cluster_summary"] = pd.read_csv(clusters_file)

    ip_clusters_file = spark_dir / "spark_clusters.csv"
    if ip_clusters_file.exists():
        res["ip_clusters"] = pd.read_csv(ip_clusters_file)

    return res
