"""Unit and integration tests for MongoDB alert storage and queries."""
import pytest
from src.database.mongodb import MongoDBManager


def test_mongodb_operations():
    db = MongoDBManager()

    test_alert = {
        "timestamp": "2026-10-09T00:50:00",
        "source_ip": "198.51.100.99",
        "destination_ip": "10.0.0.5",
        "threat_type": "DDOS",
        "threat_score": 0.95,
        "severity": "CRITICAL",
        "event_count": 9999,
        "unique_ports": 2,
        "failed_connections": 50,
        "detection_reason": "Unit test synthetic alert insertion"
    }

    # Should succeed whether MongoDB is live or in fallback mode
    inserted = db.insert_alert(test_alert)
    assert inserted is True

    recent = db.query_recent_alerts(limit=10)
    assert len(recent) > 0

    top_ips = db.get_top_suspicious_ips(limit=5)
    assert len(top_ips) > 0
