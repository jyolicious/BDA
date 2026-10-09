"""Explainable Threat Scoring Engine.

Combines multi-modal threat indicators (frequency, volumetric traffic, port scan,
and behavioral anomaly) into a normalized [0, 1] threat score and maps to discrete severity bands.
"""
from typing import Any, Dict, Optional, Tuple
from src.common.utils import load_detection_rules


class ThreatScorer:
    """Calculates explainable composite threat scores and severity classifications."""

    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or load_detection_rules()
        scoring_cfg = self.rules.get("threat_scoring", {})
        self.weights = scoring_cfg.get("weights", {
            "frequency_score": 0.25,
            "traffic_score": 0.30,
            "port_scan_score": 0.25,
            "anomaly_score": 0.20
        })

    def calculate_score(
        self,
        frequency_score: float,
        traffic_score: float,
        port_scan_score: float,
        anomaly_score: float
    ) -> Tuple[float, str, str, Dict[str, Any]]:
        """Compute composite threat score and explainable attribution.

        Combines dominant attack indicator with frequency and secondary anomalies.
        Returns:
            composite_score (float): Normalized score clamped to [0.0, 1.0]
            severity (str): LOW, MEDIUM, HIGH, or CRITICAL
            primary_threat_type (str): Dominant threat category
            explanation (dict): Weight and score component breakdown
        """
        # Determine dominant primary threat indicator
        indicators = {
            "DDOS": traffic_score,
            "PORT_SCAN": port_scan_score,
            "ANOMALY": anomaly_score
        }
        dominant_threat, max_attack_score = max(indicators.items(), key=lambda x: x[1])

        # Composite formulation: 70% dominant attack vector + 30% frequency/volume compounding
        if max_attack_score > 0.0:
            raw_score = 0.70 * max_attack_score + 0.30 * frequency_score
        else:
            raw_score = 0.20 * frequency_score

        composite_score = round(max(0.0, min(1.0, raw_score)), 4)

        # Map to severity bands
        if composite_score >= 0.80:
            severity = "CRITICAL"
        elif composite_score >= 0.60:
            severity = "HIGH"
        elif composite_score >= 0.30:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        primary_threat = dominant_threat if composite_score >= 0.30 else "NORMAL"

        explanation = {
            "composite_score": composite_score,
            "dominant_attack_vector": dominant_threat,
            "attack_indicator_score": round(max_attack_score, 4),
            "frequency_score": round(frequency_score, 4),
            "raw_inputs": {
                "frequency_score": round(frequency_score, 4),
                "traffic_score": round(traffic_score, 4),
                "port_scan_score": round(port_scan_score, 4),
                "anomaly_score": round(anomaly_score, 4)
            }
        }

        return composite_score, severity, primary_threat, explanation
