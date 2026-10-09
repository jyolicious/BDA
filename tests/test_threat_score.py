"""Unit tests for composite Threat Scorer and severity banding."""
import pytest
from src.streaming.threat_scorer import ThreatScorer


def test_threat_score_normalization():
    scorer = ThreatScorer()

    score, sev, threat_type, expl = scorer.calculate_score(
        frequency_score=1.0,
        traffic_score=1.0,
        port_scan_score=0.0,
        anomaly_score=0.0
    )
    assert 0.0 <= score <= 1.0
    assert sev in {"HIGH", "CRITICAL"}
    assert threat_type == "DDOS"
    assert "Dominant" in expl["dominant_attack_vector"] or "composite_score" in expl


def test_threat_score_low_baseline():
    scorer = ThreatScorer()

    score, sev, threat_type, expl = scorer.calculate_score(
        frequency_score=0.1,
        traffic_score=0.0,
        port_scan_score=0.0,
        anomaly_score=0.0
    )
    assert score <= 0.30
    assert sev == "LOW"
    assert threat_type == "NORMAL"
