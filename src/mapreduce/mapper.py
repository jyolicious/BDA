#!/usr/bin/env python
"""Hadoop Streaming Mapper for Cyber Threat Telemetry.

Reads raw CSV network event lines from standard input and emits
key-value pairs formatted as:
    <key>\t<value>

Supported jobs:
- ip_count:       source_ip -> 1
- attack_freq:    attack_label -> 1
- port_activity:  destination_port -> 1 (or destination_port:bytes)
"""
import sys
import argparse


def run_mapper(job_type: str = "ip_count"):
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split(",")
        # Skip CSV header row
        if parts[0] == "timestamp" or len(parts) < 12:
            continue

        source_ip = parts[1]
        destination_port = parts[4]
        attack_label = parts[11]

        if job_type == "ip_count":
            # Job 1: Event count by source IP
            sys.stdout.write(f"{source_ip}\t1\n")

        elif job_type == "attack_freq":
            # Job 2: Attack-type frequency
            sys.stdout.write(f"{attack_label}\t1\n")

        elif job_type == "port_activity":
            # Job 3: Port activity frequency
            sys.stdout.write(f"{destination_port}\t1\n")

        elif job_type == "ip_ports":
            # Auxiliary: Source IP to destination port pair
            sys.stdout.write(f"{source_ip}\t{destination_port}\n")

        else:
            sys.stdout.write(f"{source_ip}\t1\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hadoop Streaming Mapper")
    parser.add_argument(
        "--job",
        choices=["ip_count", "attack_freq", "port_activity", "ip_ports"],
        default="ip_count",
        help="Job mapping logic to execute"
    )
    args = parser.parse_args()
    run_mapper(args.job)
