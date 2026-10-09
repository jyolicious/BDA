"""Seed MongoDB with historical batch aggregates and initial threat alerts."""
import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.logger import get_logger
from src.common.utils import get_project_root
from src.database.mongodb import MongoDBManager

logger = get_logger("seed_mongodb")


def main():
    root = get_project_root()
    db = MongoDBManager()

    if not db.is_connected():
        logger.warning("MongoDB is offline or unreachable. Seeding in-memory records only.")

    logger.info("Seeding MongoDB collections with historical threat intelligence...")

    # 1. Ingest MapReduce results if present
    mr_attacks_file = root / "results" / "mapreduce" / "mapreduce_attack_counts.csv"
    if mr_attacks_file.exists():
        logger.info(f"Loading MapReduce summary from {mr_attacks_file} into MongoDB...")
        records = []
        with open(mr_attacks_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "type": "MAPREDUCE_ATTACK_DISTRIBUTION",
                    "attack_type": row["attack_type"],
                    "event_count": int(row["event_count"]),
                    "percentage": row["percentage"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        if db.is_connected() and db.db is not None:
            db.db["batch_aggregates"].delete_many({"type": "MAPREDUCE_ATTACK_DISTRIBUTION"})
            if records:
                db.db["batch_aggregates"].insert_many(records)
                logger.info(f"Inserted {len(records)} MapReduce summary records.")

    # 2. Ingest Spark clusters if present
    spark_clusters_file = root / "results" / "spark" / "cluster_summary.csv"
    if spark_clusters_file.exists():
        logger.info(f"Loading Spark cluster summaries from {spark_clusters_file} into MongoDB...")
        cluster_recs = []
        with open(spark_clusters_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cluster_recs.append({
                    "cluster_id": int(row["cluster"]),
                    "host_count": int(row["host_count"]),
                    "profile": row["assigned_profile"],
                    "severity": row["threat_severity"],
                    "mean_bytes_sent": float(row["mean_bytes_sent"]),
                    "mean_unique_ports": float(row["mean_unique_ports"]),
                    "mean_failed_conns": float(row["mean_failed_conns"]),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        if db.is_connected() and db.db is not None:
            db.db["spark_clusters"].delete_many({})
            if cluster_recs:
                db.db["spark_clusters"].insert_many(cluster_recs)
                logger.info(f"Inserted {len(cluster_recs)} Spark cluster summaries.")

    # 3. Seed Realistic Reference Threat Alerts
    base_time = datetime.now(timezone.utc)
    seed_alerts = [
        {
            "timestamp": (base_time - timedelta(minutes=12)).strftime("%Y-%m-%dT%H:%M:%S"),
            "source_ip": "185.220.101.5",
            "destination_ip": "10.0.0.5",
            "threat_type": "DDOS",
            "threat_score": 0.96,
            "severity": "CRITICAL",
            "event_count": 84231,
            "unique_ports": 2,
            "failed_connections": 124,
            "event_rate_per_sec": 420.5,
            "byte_rate_per_sec": 384000.0,
            "packet_rate_per_sec": 8400.0,
            "detection_reason": "Extreme event rate, packet volume, and byte burst targeting port 80"
        },
        {
            "timestamp": (base_time - timedelta(minutes=8)).strftime("%Y-%m-%dT%H:%M:%S"),
            "source_ip": "198.18.0.42",
            "destination_ip": "10.0.0.15",
            "threat_type": "PORT_SCAN",
            "threat_score": 0.82,
            "severity": "CRITICAL",
            "event_count": 1420,
            "unique_ports": 284,
            "failed_connections": 268,
            "event_rate_per_sec": 145.0,
            "byte_rate_per_sec": 12400.0,
            "packet_rate_per_sec": 290.0,
            "detection_reason": "Rapid horizontal port sweep across 284 ports with 94.4% connection drops"
        },
        {
            "timestamp": (base_time - timedelta(minutes=4)).strftime("%Y-%m-%dT%H:%M:%S"),
            "source_ip": "172.16.50.89",
            "destination_ip": "10.0.0.20",
            "threat_type": "ANOMALY",
            "threat_score": 0.74,
            "severity": "HIGH",
            "event_count": 520,
            "unique_ports": 4,
            "failed_connections": 12,
            "event_rate_per_sec": 65.0,
            "byte_rate_per_sec": 890000.0,
            "packet_rate_per_sec": 620.0,
            "detection_reason": "High byte exfiltration asymmetry (2.4 MB sent) on covert port 4444"
        },
        {
            "timestamp": (base_time - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            "source_ip": "194.26.29.11",
            "destination_ip": "10.0.0.5",
            "threat_type": "DDOS",
            "threat_score": 0.88,
            "severity": "CRITICAL",
            "event_count": 42100,
            "unique_ports": 1,
            "failed_connections": 88,
            "event_rate_per_sec": 310.0,
            "byte_rate_per_sec": 295000.0,
            "packet_rate_per_sec": 6100.0,
            "detection_reason": "Volumetric SYN flood attack concentrated on HTTPS port 443"
        }
    ]

    for alert in seed_alerts:
        db.insert_alert(alert)

    logger.info(f"Seeded {len(seed_alerts)} baseline threat alerts successfully into MongoDB.")
    print("\n--- MONGODB SEEDING COMPLETE ---")
    print(f"Database:     {db.db_name}")
    print(f"Collections:  threat_alerts, streaming_events, batch_aggregates, spark_clusters")
    print(f"Alerts Count: {len(db.query_recent_alerts(limit=100))}")
    print("--------------------------------\n")


if __name__ == "__main__":
    main()
