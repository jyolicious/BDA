"""Unit tests for DDoS, Port Scan, and Anomaly threat detection engines."""
import pytest
from src.streaming.detectors import ThreatDetectionEngine


def test_ddos_detector_trigger():
    engine = ThreatDetectionEngine()

    ddos_metrics = {
        "event_count": 150,
        "event_rate_per_sec": 35.0,
        "packet_rate_per_sec": 850.0,
        "byte_rate_per_sec": 450000.0,
        "unique_dest_ports": 2
    }
    triggered, score, reason = engine.evaluate_ddos(ddos_metrics)
    assert triggered is True
    assert score >= 0.70
    assert "DDoS" in reason


def test_port_scan_detector_trigger():
    engine = ThreatDetectionEngine()

    scan_metrics = {
        "event_count": 45,
        "unique_dest_ports": 35,
        "failed_connections": 32,
        "failed_ratio": 0.71
    }
    triggered, score, reason = engine.evaluate_port_scan(scan_metrics)
    assert triggered is True
    assert score >= 0.60
    assert "Port scan" in reason


def test_normal_traffic_clean():
    engine = ThreatDetectionEngine()

    normal_metrics = {
        "event_count": 10,
        "event_rate_per_sec": 2.0,
        "packet_rate_per_sec": 20.0,
        "byte_rate_per_sec": 5000.0,
        "unique_dest_ports": 2,
        "failed_connections": 0,
        "failed_ratio": 0.0,
        "bytes_sent": 4000,
        "bytes_received": 15000
    }
    ddos_trig, _, _ = engine.evaluate_ddos(normal_metrics)
    scan_trig, _, _ = engine.evaluate_port_scan(normal_metrics)
    assert ddos_trig is False
    assert scan_trig is False
