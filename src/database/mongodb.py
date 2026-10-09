"""MongoDB Storage Manager for High-Volume Cyber Threat Intelligence and Alerts."""
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pymongo
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from src.common.logger import get_logger
from src.common.utils import load_config

logger = get_logger("mongodb_manager")


class MongoDBManager:
    """Manages document storage, indexes, and queries for cybersecurity telemetry and alerts."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_config()
        db_cfg = self.config.get("database", {})
        self.mongo_uri = os.environ.get("MONGO_URI", db_cfg.get("mongo_uri", "mongodb://localhost:27017/"))
        self.db_name = db_cfg.get("db_name", "cyber_threat_intelligence")

        colls = db_cfg.get("collections", {})
        self.alerts_col_name = colls.get("alerts", "threat_alerts")
        self.events_col_name = colls.get("events", "streaming_events")

        self.client: Optional[MongoClient] = None
        self.db = None
        self.alerts_col = None
        self.events_col = None
        self._connected = False

        # In-memory buffer fallback in case MongoDB server drops offline
        self._memory_alerts: List[Dict[str, Any]] = []

        self.connect()

    def connect(self) -> bool:
        """Establish connection and provision collection indexes."""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2500)
            # Force server check
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.alerts_col = self.db[self.alerts_col_name]
            self.events_col = self.db[self.events_col_name]
            self._connected = True

            self._create_indexes()
            logger.info(f"Connected to MongoDB database '{self.db_name}' at {self.mongo_uri}")
            return True

        except (ConnectionFailure, PyMongoError) as ex:
            self._connected = False
            logger.warning(
                f"MongoDB connection failed at {self.mongo_uri}: {ex}. "
                "Operating with resilient in-memory alert buffer."
            )
            return False

    def is_connected(self) -> bool:
        """Return True if active live connection to MongoDB is established."""
        return self._connected

    def _create_indexes(self) -> None:
        """Build indexes for timestamp, source IP, severity, and threat type."""
        if not self._connected or self.alerts_col is None:
            return

        try:
            # Alerts indexes
            self.alerts_col.create_index([("timestamp", DESCENDING)])
            self.alerts_col.create_index([("source_ip", ASCENDING)])
            self.alerts_col.create_index([("severity", ASCENDING)])
            self.alerts_col.create_index([("threat_type", ASCENDING)])
            self.alerts_col.create_index([("threat_score", DESCENDING)])
            # Compound index
            self.alerts_col.create_index([("source_ip", ASCENDING), ("timestamp", DESCENDING)])

            # Events indexes
            self.events_col.create_index([("timestamp", DESCENDING)])
            self.events_col.create_index([("source_ip", ASCENDING)])
            logger.info("Verified all MongoDB indexes on threat_alerts and streaming_events.")
        except Exception as e:
            logger.warning(f"Error creating MongoDB indexes: {e}")

    def insert_alert(self, alert_doc: Dict[str, Any]) -> bool:
        """Persist a detected threat alert document into MongoDB."""
        if "created_at" not in alert_doc:
            alert_doc["created_at"] = datetime.now(timezone.utc)

        if self._connected and self.alerts_col is not None:
            try:
                self.alerts_col.insert_one(alert_doc)
                return True
            except Exception as e:
                logger.error(f"Failed to insert alert into MongoDB: {e}")
                self._memory_alerts.append(alert_doc)
                return False
        else:
            self._memory_alerts.append(alert_doc)
            return True

    def insert_events_batch(self, events: List[Dict[str, Any]]) -> int:
        """Batch insert raw streaming network events."""
        if not events:
            return 0
        if self._connected and self.events_col is not None:
            try:
                res = self.events_col.insert_many(events, ordered=False)
                return len(res.inserted_ids)
            except Exception as e:
                logger.error(f"Failed to batch insert events: {e}")
                return 0
        return len(events)

    def query_recent_alerts(self, limit: int = 50, min_severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve latest threat alerts ordered by recency."""
        query = {}
        if min_severity:
            sev_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            target_rank = sev_rank.get(min_severity, 1)
            allowed = [k for k, v in sev_rank.items() if v >= target_rank]
            query["severity"] = {"$in": allowed}

        if self._connected and self.alerts_col is not None:
            try:
                docs = list(self.alerts_col.find(query, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit))
                return docs
            except Exception as e:
                logger.error(f"Error querying MongoDB alerts: {e}")

        # Fallback to in-memory buffer
        filtered = [a for a in self._memory_alerts if not min_severity or a.get("severity") == min_severity]
        return sorted(filtered, key=lambda x: str(x.get("timestamp", "")), reverse=True)[:limit]

    def get_top_suspicious_ips(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Aggregate top suspicious IPs ranked by threat score and total detected events."""
        if self._connected and self.alerts_col is not None:
            pipeline = [
                {
                    "$group": {
                        "_id": "$source_ip",
                        "max_threat_score": {"$max": "$threat_score"},
                        "latest_severity": {"$last": "$severity"},
                        "threat_types": {"$addToSet": "$threat_type"},
                        "alert_count": {"$sum": 1},
                        "total_event_volume": {"$max": "$event_count"},
                        "last_seen": {"$max": "$timestamp"}
                    }
                },
                {"$sort": {"max_threat_score": -1, "alert_count": -1}},
                {"$limit": limit},
                {
                    "$project": {
                        "_id": 0,
                        "source_ip": "$_id",
                        "threat_score": "$max_threat_score",
                        "severity": "$latest_severity",
                        "threat_types": "$threat_types",
                        "alert_count": "$alert_count",
                        "event_count": "$total_event_volume",
                        "last_seen": "$last_seen"
                    }
                }
            ]
            try:
                return list(self.alerts_col.aggregate(pipeline))
            except Exception as e:
                logger.error(f"Error running top suspicious IPs aggregation: {e}")

        # In-memory aggregation fallback
        ip_map = {}
        for a in self._memory_alerts:
            ip = a["source_ip"]
            if ip not in ip_map or a["threat_score"] > ip_map[ip]["threat_score"]:
                ip_map[ip] = {
                    "source_ip": ip,
                    "threat_score": a.get("threat_score", 0.0),
                    "severity": a.get("severity", "LOW"),
                    "threat_types": [a.get("threat_type", "UNKNOWN")],
                    "alert_count": 1,
                    "event_count": a.get("event_count", 1),
                    "last_seen": a.get("timestamp", "")
                }
        sorted_ips = sorted(ip_map.values(), key=lambda x: x["threat_score"], reverse=True)
        return sorted_ips[:limit]

    def get_threat_distribution(self) -> Dict[str, int]:
        """Return counts of alerts categorized by threat type."""
        dist = {"DDOS": 0, "PORT_SCAN": 0, "ANOMALY": 0, "HIGH_VOLUME": 0}
        if self._connected and self.alerts_col is not None:
            pipeline = [
                {"$group": {"_id": "$threat_type", "count": {"$sum": 1}}}
            ]
            try:
                for item in self.alerts_col.aggregate(pipeline):
                    dist[str(item["_id"])] = item["count"]
                return dist
            except Exception as e:
                logger.error(f"Error getting threat distribution: {e}")

        for a in self._memory_alerts:
            t = a.get("threat_type", "OTHER")
            dist[t] = dist.get(t, 0) + 1
        return dist

    def clear_database(self) -> None:
        """Clear alerts and events collections for clean demonstration restarts."""
        if self._connected and self.db is not None:
            try:
                self.alerts_col.delete_many({})
                self.events_col.delete_many({})
                logger.info("Cleared MongoDB alerts and events collections.")
            except Exception as e:
                logger.error(f"Failed to clear MongoDB: {e}")
        self._memory_alerts.clear()
