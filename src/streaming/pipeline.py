"""Streaming Cyber Threat Detection Pipeline Engine.

Orchestrates the real-time processing flow:
Network Event -> Bloom Filter -> Frequent Item Tracker -> Sliding Window ->
Threat Detectors -> Threat Scorer -> MongoDB Storage & Real-Time Alerts.
"""
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from src.common.logger import get_logger
from src.common.utils import load_config
from src.data.schema import NetworkEvent
from src.database.mongodb import MongoDBManager
from src.streaming.bloom_filter import BloomFilter
from src.streaming.detectors import ThreatDetectionEngine
from src.streaming.frequent_items import FrequentItemTracker
from src.streaming.sliding_window import SlidingWindowTracker
from src.streaming.threat_scorer import ThreatScorer

logger = get_logger("streaming_pipeline")


class StreamingPipeline:
    """Integrated streaming threat intelligence engine."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        db_manager: Optional[MongoDBManager] = None,
        on_alert_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.config = config or load_config()
        self.db = db_manager or MongoDBManager(self.config)
        self.on_alert = on_alert_callback

        stream_cfg = self.config.get("streaming", {})
        win_size = stream_cfg.get("window_size_seconds", 300)
        bf_cfg = stream_cfg.get("bloom_filter", {})

        # Components
        self.bloom_filter = BloomFilter(
            capacity=bf_cfg.get("expected_elements", 1000000),
            error_rate=bf_cfg.get("false_positive_rate", 0.01)
        )
        self.frequent_items = FrequentItemTracker(max_tracked=100)
        self.sliding_window = SlidingWindowTracker(window_size_seconds=win_size)
        self.detectors = ThreatDetectionEngine()
        self.threat_scorer = ThreatScorer()

        # Telemetry & State
        self.events_processed = 0
        self.threats_detected = 0
        self.critical_alerts = 0
        self.start_time = time.time()
        self.recent_alerts: List[Dict[str, Any]] = []
        self.traffic_history: List[Dict[str, Any]] = []  # Time-series buckets for charts

        # Cooldown tracker to prevent alert flooding per IP: ip -> last_alert_time
        self._alert_cooldowns: Dict[str, float] = {}

    def process_event(self, event: NetworkEvent) -> Optional[Dict[str, Any]]:
        """Process an individual network telemetry event through the streaming pipeline."""
        now = time.time()
        self.events_processed += 1

        # 1. Bloom Filter Membership Test
        ip = event.source_ip
        is_returning_ip = self.bloom_filter.contains(ip)
        self.bloom_filter.add(ip)

        # 2. Frequent Items / Heavy-Hitters Update
        self.frequent_items.update(ip)

        # 3. Sliding Window Ingestion & Pruning
        self.sliding_window.add_event(event)

        # 4. Host Feature Aggregation from Window
        metrics = self.sliding_window.get_host_metrics(ip)
        if not metrics:
            return None

        # 5. Multi-Detector Behavioral Evaluation
        is_ddos, ddos_score, ddos_reason = self.detectors.evaluate_ddos(metrics)
        is_ps, ps_score, ps_reason = self.detectors.evaluate_port_scan(metrics)
        is_anom, anom_score, anom_reason = self.detectors.evaluate_anomaly(metrics, event)
        freq_score = self.detectors.evaluate_frequency(metrics)

        # 6. Composite Threat Scoring
        threat_score, severity, threat_type, explanation = self.threat_scorer.calculate_score(
            frequency_score=freq_score,
            traffic_score=ddos_score,
            port_scan_score=ps_score,
            anomaly_score=anom_score
        )

        alert = None
        # 7. Threat Triggering and Alert Persistence
        # Trigger if score is HIGH/CRITICAL or any detector explicitly fired
        is_threat = (severity in {"HIGH", "CRITICAL"}) or (threat_score >= 0.60) or is_ddos or is_ps

        if is_threat:
            last_alerted = self._alert_cooldowns.get(ip, 0.0)
            # Throttle alerts to once every 2 seconds per IP
            if (now - last_alerted) > 2.0:
                self._alert_cooldowns[ip] = now
                self.threats_detected += 1
                if severity == "CRITICAL":
                    self.critical_alerts += 1

                # Construct primary reason
                if is_ddos:
                    reason = ddos_reason
                elif is_ps:
                    reason = ps_reason
                elif is_anom:
                    reason = anom_reason
                else:
                    reason = f"High behavioral threat score: {threat_score:.2f} ({severity})"

                alert = {
                    "timestamp": event.timestamp,
                    "source_ip": ip,
                    "destination_ip": event.destination_ip,
                    "threat_type": threat_type if threat_type != "NORMAL" else ("DDOS" if is_ddos else ("PORT_SCAN" if is_ps else "ANOMALY")),
                    "threat_score": threat_score,
                    "severity": severity,
                    "event_count": metrics["event_count"],
                    "unique_ports": metrics["unique_dest_ports"],
                    "failed_connections": metrics["failed_connections"],
                    "event_rate_per_sec": metrics["event_rate_per_sec"],
                    "byte_rate_per_sec": metrics["byte_rate_per_sec"],
                    "packet_rate_per_sec": metrics["packet_rate_per_sec"],
                    "detection_reason": reason,
                    "score_breakdown": explanation
                }

                # Persist to MongoDB
                self.db.insert_alert(alert)

                # Keep in circular alert memory
                self.recent_alerts.append(alert)
                if len(self.recent_alerts) > 100:
                    self.recent_alerts.pop(0)

                # User callback (e.g. for dashboard live push or logger)
                if self.on_alert:
                    self.on_alert(alert)

        return alert

    def get_pipeline_telemetry(self) -> Dict[str, Any]:
        """Return operational pipeline statistics for dashboard display."""
        uptime = max(time.time() - self.start_time, 1.0)
        eps = round(self.events_processed / uptime, 1)

        win_stats = self.sliding_window.get_window_stats()
        bf_stats = self.bloom_filter.get_stats()
        top_frequent = self.frequent_items.get_top_k(10)

        return {
            "uptime_seconds": round(uptime, 1),
            "events_processed": self.events_processed,
            "events_per_second": eps,
            "threats_detected": self.threats_detected,
            "critical_alerts": self.critical_alerts,
            "active_window_events": win_stats["active_events_in_window"],
            "active_unique_ips": win_stats["active_unique_ips"],
            "bloom_filter": bf_stats,
            "top_frequent_ips": top_frequent,
            "mongodb_connected": self.db.is_connected()
        }
