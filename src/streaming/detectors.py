"""Threat Detection Engines for Streaming Network Intelligence.

Implements three detection mechanisms evaluated against host sliding-window state:
1. Volumetric DDoS-like Traffic Detector
2. Horizontal/Vertical Port Scan Detector
3. Statistical Behavior Anomaly Detector
"""
from typing import Any, Dict, Optional, Tuple
from src.common.utils import load_detection_rules


class ThreatDetectionEngine:
    """Evaluates host streaming behavioral telemetry against configurable cybersecurity rules."""

    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or load_detection_rules()
        self.ddos_cfg = self.rules.get("ddos_detector", {})
        self.port_scan_cfg = self.rules.get("port_scan_detector", {})
        self.anomaly_cfg = self.rules.get("anomaly_detector", {})
        self.freq_cfg = self.rules.get("frequency_detector", {})

    def evaluate_ddos(self, metrics: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Detect volumetric flood attacks based on event rate, packet rate, and byte burst."""
        min_ev_cnt = self.ddos_cfg.get("min_event_count", 80)
        min_ev_rate = self.ddos_cfg.get("min_event_rate_per_sec", 15.0)
        min_pkt_rate = self.ddos_cfg.get("min_packet_rate_per_sec", 300.0)
        min_byte_rate = self.ddos_cfg.get("min_byte_rate_per_sec", 150000.0)

        ev_count = metrics["event_count"]
        ev_rate = metrics["event_rate_per_sec"]
        pkt_rate = metrics["packet_rate_per_sec"]
        byte_rate = metrics["byte_rate_per_sec"]
        ports = metrics["unique_dest_ports"]

        # Score components normalized between 0.0 and 1.0
        score_rate = min(ev_rate / (min_ev_rate * 2.0), 1.0)
        score_bytes = min(byte_rate / (min_byte_rate * 2.0), 1.0)
        score_pkts = min(pkt_rate / (min_pkt_rate * 2.0), 1.0)

        # Port concentration factor: DDoS attacks usually hit 1 to 3 service ports
        concentration = 1.0 if ports <= 3 else (0.5 if ports <= 6 else 0.1)

        ddos_score = round(0.4 * score_rate + 0.3 * score_bytes + 0.3 * score_pkts, 4) * concentration

        triggered = (
            ev_count >= min_ev_cnt
            and (ev_rate >= min_ev_rate or pkt_rate >= min_pkt_rate or byte_rate >= min_byte_rate)
            and ports <= 6
        )

        reason = (
            f"DDoS volumetric flood: {ev_rate:.1f} ev/s, {pkt_rate:.1f} pkts/s, "
            f"{byte_rate/1024:.1f} KB/s targeted across {ports} ports."
            if triggered else "Normal flow density"
        )

        return triggered, min(ddos_score, 1.0), reason

    def evaluate_port_scan(self, metrics: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Detect port scan/reconnaissance based on port diversity and connection rejection ratios."""
        min_ports = self.port_scan_cfg.get("min_unique_ports", 15)
        min_failed_ratio = self.port_scan_cfg.get("min_failed_connection_ratio", 0.50)
        min_ev_cnt = self.port_scan_cfg.get("min_event_count", 20)

        unique_ports = metrics["unique_dest_ports"]
        failed_ratio = metrics["failed_ratio"]
        ev_count = metrics["event_count"]

        # Port scan score
        port_score = min(unique_ports / (min_ports * 2.0), 1.0)
        failure_score = min(failed_ratio / 0.8, 1.0)
        port_scan_score = round(0.6 * port_score + 0.4 * failure_score, 4)

        triggered = (
            unique_ports >= min_ports
            and failed_ratio >= min_failed_ratio
            and ev_count >= min_ev_cnt
        )

        reason = (
            f"Port scan reconnaissance: {unique_ports} unique ports probed with "
            f"{failed_ratio*100:.1f}% connection failures ({metrics['failed_connections']} rejected)."
            if triggered else "Standard port interaction"
        )

        return triggered, min(port_scan_score, 1.0), reason

    def evaluate_anomaly(self, metrics: Dict[str, Any], event: Optional[Any] = None) -> Tuple[bool, float, str]:
        """Detect statistical behavioral deviations, data exfiltration, or covert communications."""
        min_asymm = self.anomaly_cfg.get("min_byte_ratio_asymmetry", 10.0)
        unusual_ports = set(self.anomaly_cfg.get("unusual_ports", [4444, 6667, 1337, 31337, 9999]))

        bytes_sent = metrics["bytes_sent"]
        bytes_recv = max(metrics["bytes_received"], 1)
        asymmetry_ratio = bytes_sent / float(bytes_recv)

        has_unusual_port = False
        if event and getattr(event, "destination_port", None) in unusual_ports:
            has_unusual_port = True

        anomaly_score = 0.0
        reasons = []

        if bytes_sent > 250000 and asymmetry_ratio >= min_asymm:
            anomaly_score += 0.60
            reasons.append(f"Severe exfiltration asymmetry (sent/recv: {asymmetry_ratio:.1f}x)")

        if has_unusual_port:
            anomaly_score += 0.40
            reasons.append(f"Covert port access: {getattr(event, 'destination_port', '')}")

        anomaly_score = min(anomaly_score, 1.0)
        triggered = anomaly_score >= 0.50
        reason_str = "; ".join(reasons) if triggered else "Baseline traffic conformity"

        return triggered, round(anomaly_score, 4), reason_str

    def evaluate_frequency(self, metrics: Dict[str, Any]) -> float:
        """Normalized frequency / volume score [0.0 - 1.0]."""
        high_thresh = float(self.freq_cfg.get("high_frequency_threshold", 100.0))
        return min(metrics["event_count"] / high_thresh, 1.0)
