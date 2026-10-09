"""Automated Academic Demo Script for Cyber Threat Detection Pipeline.

Executes a deterministic sequence demonstrating:
1. Baseline Normal Traffic
2. Volumetric DDoS Flood Attack (triggers CRITICAL alert)
3. Return to Baseline
4. Port-Scan Reconnaissance Attack (triggers HIGH alert)
5. Statistical Anomaly & Data Exfiltration (triggers alert)
6. Normal Baseline Recovery & Final Report
"""
import argparse
import csv
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.logger import get_logger
from src.common.utils import get_project_root
from src.database.mongodb import MongoDBManager
from src.streaming.event_producer import StreamingEventProducer
from src.streaming.pipeline import StreamingPipeline

logger = get_logger("demo_orchestrator")


def parse_args():
    parser = argparse.ArgumentParser(description="Deterministic Academic Live Demo Orchestrator.")
    parser.add_argument(
        "--step-duration", "-s",
        type=int,
        default=5,
        help="Duration in seconds for each phase of the attack sequence."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    step_duration = args.step_duration
    root = get_project_root()
    output_alerts_csv = root / "results" / "streaming" / "streaming_alerts.csv"
    output_alerts_csv.parent.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 68)
    print("      ACADEMIC LIVE DEMO: BIG DATA CYBER THREAT DETECTION      ")
    print("=" * 68)
    print(f"Phase Duration: {step_duration} seconds per scenario step")
    print(f"MongoDB Target: localhost:27017")
    print("=" * 68 + "\n")

    db = MongoDBManager()
    captured_alerts = []

    def on_alert(alert):
        captured_alerts.append(alert)
        color = "\033[91m" if alert["severity"] == "CRITICAL" else "\033[33m"
        reset = "\033[0m"
        print(f"  {color}>>> TRIGGERED ALERT: [{alert['severity']}] {alert['threat_type']}{reset}")
        print(f"      Host: {alert['source_ip']} | Score: {alert['threat_score']:.2f}")
        print(f"      Reason: {alert['detection_reason']}")

    pipeline = StreamingPipeline(db_manager=db, on_alert_callback=on_alert)
    producer = StreamingEventProducer(mode="NORMAL")

    producer.start_streaming(on_event_callback=pipeline.process_event)

    phases = [
        ("PHASE 1: Baseline Normal Workload", "NORMAL", "Establishing baseline telemetry. No critical alerts expected."),
        ("PHASE 2: Volumetric DDoS Simulation", "DDOS", "Simulating high-rate packet flood. Expecting CRITICAL DDoS alert."),
        ("PHASE 3: Normal Traffic Recovery", "NORMAL", "Traffic returning to safe parameters."),
        ("PHASE 4: Port Scan Reconnaissance", "PORT_SCAN", "Simulating port sweep with connection rejections. Expecting HIGH Port-Scan alert."),
        ("PHASE 5: Covert Channel / Anomaly", "ANOMALY", "Simulating asymmetric data exfiltration on non-standard ports."),
        ("PHASE 6: Return to Baseline", "NORMAL", "Cooldown and final stabilization.")
    ]

    for phase_name, mode, desc in phases:
        print(f"\n---> {phase_name}")
        print(f"     Profile: {mode:<10} | {desc}")
        producer.set_mode(mode)

        start_step = time.time()
        while time.time() - start_step < step_duration:
            time.sleep(1.0)
            tel = pipeline.get_pipeline_telemetry()
            print(
                f"     [Status] Mode: {mode:<9} | Processed: {tel['events_processed']:<5} "
                f"({tel['events_per_second']:>5.1f} ev/s) | Active Window: {tel['active_window_events']:<4} | Alerts: {tel['threats_detected']}"
            )

    producer.stop_streaming()

    # Save alerts
    if captured_alerts:
        with open(output_alerts_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "source_ip", "threat_type", "threat_score",
                "severity", "event_count", "unique_ports", "failed_connections",
                "detection_reason"
            ])
            for a in captured_alerts:
                writer.writerow([
                    a["timestamp"], a["source_ip"], a["threat_type"], a["threat_score"],
                    a["severity"], a["event_count"], a["unique_ports"], a["failed_connections"],
                    a["detection_reason"]
                ])

    final_tel = pipeline.get_pipeline_telemetry()
    bf = final_tel["bloom_filter"]

    print("\n" + "=" * 68)
    print("                     DEMONSTRATION SUMMARY                     ")
    print("=" * 68)
    print(f"Total Stream Events Processed: {final_tel['events_processed']:,}")
    print(f"Total Threats Identified:      {final_tel['threats_detected']}")
    print(f"Critical Alerts Fired:         {final_tel['critical_alerts']}")
    print(f"Bloom Filter Unique Entries:   {bf['elements_added']}")
    print(f"Bloom Filter Memory Size:      {bf['memory_usage_kb']:.2f} KB")
    print(f"Bloom Filter Current FPP:      {bf['current_fpp']:.6f}")
    print(f"Alerts Exported To:            {output_alerts_csv}")
    print(f"MongoDB Live Status:           {'CONNECTED' if final_tel['mongodb_connected'] else 'OFFLINE'}")
    print("=" * 68 + "\n")


if __name__ == "__main__":
    main()
