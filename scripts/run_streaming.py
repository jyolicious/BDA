"""CLI Script for Real-Time Streaming Cyber Threat Detection."""
import argparse
import csv
import signal
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

logger = get_logger("streaming_cli")


def parse_args():
    parser = argparse.ArgumentParser(description="Real-Time Streaming Cyber Threat Detector.")
    parser.add_argument(
        "--mode", "-m",
        choices=["normal", "ddos", "port_scan", "anomaly"],
        default="normal",
        help="Traffic profile generation mode (normal, ddos, port_scan, anomaly)."
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=0,
        help="Duration in seconds to stream (0 for continuous streaming until Ctrl+C)."
    )
    parser.add_argument(
        "--rate", "-r",
        type=float,
        default=None,
        help="Custom event emission rate (events/second)."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = get_project_root()
    output_alerts_csv = root / "results" / "streaming" / "streaming_alerts.csv"
    output_alerts_csv.parent.mkdir(parents=True, exist_ok=True)

    print("\n=======================================================")
    print("       REAL-TIME STREAMING CYBER THREAT DETECTOR       ")
    print("=======================================================")
    print(f"Simulation Mode:  {args.mode.upper()}")
    print(f"Duration:         {'Infinite (Ctrl+C to stop)' if args.duration == 0 else f'{args.duration}s'}")
    print(f"Alerts File:      {output_alerts_csv}\n")

    db = MongoDBManager()
    all_captured_alerts = []

    def on_alert_detected(alert):
        all_captured_alerts.append(alert)
        sev_color = {
            "CRITICAL": "\033[91m",
            "HIGH": "\033[33m",
            "MEDIUM": "\033[36m",
            "LOW": "\033[32m"
        }.get(alert["severity"], "")
        reset_color = "\033[0m"

        msg = (
            f" [ALERT] [{alert['severity']:<8}] {alert['threat_type']:<10} "
            f"Src: {alert['source_ip']:<15} Score: {alert['threat_score']:.2f} | {alert['detection_reason']}"
        )
        print(f"{sev_color}{msg}{reset_color}")

    pipeline = StreamingPipeline(db_manager=db, on_alert_callback=on_alert_detected)
    producer = StreamingEventProducer(mode=args.mode, custom_rate=args.rate)

    is_interrupted = False

    def handle_sigint(sig, frame):
        nonlocal is_interrupted
        is_interrupted = True

    signal.signal(signal.SIGINT, handle_sigint)

    producer.start_streaming(on_event_callback=pipeline.process_event)

    start_time = time.time()
    last_print = time.time()

    try:
        while not is_interrupted:
            time.sleep(0.5)
            elapsed = time.time() - start_time

            if time.time() - last_print >= 2.0:
                last_print = time.time()
                tel = pipeline.get_pipeline_telemetry()
                bf = tel["bloom_filter"]
                print(
                    f"[STREAM] Evs: {tel['events_processed']:<6} | {tel['events_per_second']:>5.1f} ev/s | "
                    f"Win: {tel['active_window_events']:<5} | Threats: {tel['threats_detected']:<3} | "
                    f"Crit: {tel['critical_alerts']:<3} | Bloom Entries: {bf['elements_added']:<5} | FPP: {bf['current_fpp']:.4f}"
                )

            if args.duration > 0 and elapsed >= args.duration:
                break

    finally:
        producer.stop_streaming()
        print("\nStopping streaming pipeline...")

        # Export captured alerts to CSV
        if all_captured_alerts:
            with open(output_alerts_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "source_ip", "threat_type", "threat_score",
                    "severity", "event_count", "unique_ports", "failed_connections",
                    "event_rate_per_sec", "byte_rate_per_sec", "detection_reason"
                ])
                for a in all_captured_alerts:
                    writer.writerow([
                        a["timestamp"], a["source_ip"], a["threat_type"], a["threat_score"],
                        a["severity"], a["event_count"], a["unique_ports"], a["failed_connections"],
                        a.get("event_rate_per_sec", 0), a.get("byte_rate_per_sec", 0), a["detection_reason"]
                    ])
            print(f"Saved {len(all_captured_alerts)} live threat alerts to {output_alerts_csv}")

        print("=======================================================\n")


if __name__ == "__main__":
    main()
