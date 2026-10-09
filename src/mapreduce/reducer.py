#!/usr/bin/env python
"""Hadoop Streaming Reducer for Cyber Threat Telemetry.

Reads pre-sorted key-value pairs formatted as:
    <key>\t<value>
from standard input and aggregates metrics per key.
"""
import sys
import argparse


def run_reducer(job_type: str = "ip_count"):
    current_key = None
    current_count = 0
    unique_set = set()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        key, val = parts[0], parts[1]

        if job_type in ["ip_count", "attack_freq", "port_activity"]:
            try:
                count = int(val)
            except ValueError:
                count = 1

            if current_key == key:
                current_count += count
            else:
                if current_key is not None:
                    sys.stdout.write(f"{current_key}\t{current_count}\n")
                current_key = key
                current_count = count

        elif job_type == "ip_ports":
            if current_key == key:
                unique_set.add(val)
            else:
                if current_key is not None:
                    sys.stdout.write(f"{current_key}\t{len(unique_set)}\n")
                current_key = key
                unique_set = {val}

    # Output final accumulated record
    if current_key is not None:
        if job_type in ["ip_count", "attack_freq", "port_activity"]:
            sys.stdout.write(f"{current_key}\t{current_count}\n")
        elif job_type == "ip_ports":
            sys.stdout.write(f"{current_key}\t{len(unique_set)}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hadoop Streaming Reducer")
    parser.add_argument(
        "--job",
        choices=["ip_count", "attack_freq", "port_activity", "ip_ports"],
        default="ip_count",
        help="Job aggregation logic to execute"
    )
    args = parser.parse_args()
    run_reducer(args.job)
