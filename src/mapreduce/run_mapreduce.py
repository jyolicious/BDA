"""Hadoop MapReduce Job Runner & Orchestrator.

Implements the complete Map -> Shuffle & Sort -> Reduce execution pipeline
strictly adhering to Hadoop streaming architecture.
"""
import csv
import io
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
from src.common.logger import get_logger
from src.common.utils import get_project_root

logger = get_logger("mapreduce_runner")


def execute_mapreduce_job(
    input_file: Path,
    output_file: Path,
    job_type: str = "ip_count"
) -> Dict[str, Any]:
    """Execute a single Hadoop MapReduce job following the Map-Sort-Reduce protocol."""
    start_time = time.time()
    logger.info(f"Starting MapReduce Job [{job_type}] on {input_file.name}...")

    mapper_path = Path(__file__).resolve().parent / "mapper.py"
    reducer_path = Path(__file__).resolve().parent / "reducer.py"

    py_exe = sys.executable

    # Phase 1: Map Phase
    map_proc = subprocess.Popen(
        [py_exe, str(mapper_path), "--job", job_type],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    with open(input_file, "r", encoding="utf-8") as f_in:
        map_out, map_err = map_proc.communicate(input=f_in.read())

    if map_proc.returncode != 0:
        raise RuntimeError(f"Mapper failed: {map_err}")

    # Phase 2: Partition, Shuffle & Sort Phase
    # In Hadoop, intermediate keys are sorted across partitions
    mapped_lines = [line for line in map_out.strip().split("\n") if line]
    sorted_intermediate = sorted(mapped_lines)
    sorted_input_text = "\n".join(sorted_intermediate) + "\n"

    # Phase 3: Reduce Phase
    reduce_proc = subprocess.Popen(
        [py_exe, str(reducer_path), "--job", job_type],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    reduce_out, reduce_err = reduce_proc.communicate(input=sorted_input_text)
    if reduce_proc.returncode != 0:
        raise RuntimeError(f"Reducer failed: {reduce_err}")

    # Write final output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write(reduce_out)

    elapsed = time.time() - start_time
    output_records = len([l for l in reduce_out.strip().split("\n") if l])

    logger.info(
        f"MapReduce Job [{job_type}] completed in {elapsed:.3f}s. "
        f"Intermediate mapped pairs: {len(mapped_lines):,}, Reduced keys: {output_records:,}."
    )

    return {
        "job_type": job_type,
        "elapsed_seconds": elapsed,
        "input_records": len(mapped_lines),
        "output_records": output_records,
        "output_file": str(output_file)
    }


def run_all_mapreduce_jobs(
    input_file: Path,
    results_dir: Path
) -> Dict[str, Any]:
    """Execute all required MapReduce jobs and format structured CSV summaries."""
    results_dir.mkdir(parents=True, exist_ok=True)
    summary = {}

    # Job 1: Event count by source IP
    j1_tsv = results_dir / "job1_ip_counts.tsv"
    j1_res = execute_mapreduce_job(input_file, j1_tsv, job_type="ip_count")
    summary["job1_ip_count"] = j1_res

    # Job 2: Attack-type frequency
    j2_tsv = results_dir / "job2_attack_frequencies.tsv"
    j2_res = execute_mapreduce_job(input_file, j2_tsv, job_type="attack_freq")
    summary["job2_attack_freq"] = j2_res

    # Job 3: Port activity frequency
    j3_tsv = results_dir / "job3_port_activity.tsv"
    j3_res = execute_mapreduce_job(input_file, j3_tsv, job_type="port_activity")
    summary["job3_port_activity"] = j3_res

    # Job 4: IP destination port diversity
    j4_tsv = results_dir / "job4_ip_port_diversity.tsv"
    j4_res = execute_mapreduce_job(input_file, j4_tsv, job_type="ip_ports")
    summary["job4_ip_port_diversity"] = j4_res

    # Generate polished CSV files for direct inspection and dashboarding
    # 1. mapreduce_top_ips.csv (sorted by event count descending)
    ip_records: List[Tuple[str, int]] = []
    with open(j1_tsv, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                p = line.strip().split("\t")
                if len(p) == 2:
                    ip_records.append((p[0], int(p[1])))
    ip_records.sort(key=lambda x: x[1], reverse=True)

    top_ips_csv = results_dir / "mapreduce_top_ips.csv"
    with open(top_ips_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_ip", "event_count", "volume_rank"])
        for rank, (ip, count) in enumerate(ip_records, 1):
            writer.writerow([ip, count, rank])

    # 2. mapreduce_attack_counts.csv
    attack_records: List[Tuple[str, int]] = []
    with open(j2_tsv, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                p = line.strip().split("\t")
                if len(p) == 2:
                    attack_records.append((p[0], int(p[1])))
    attack_records.sort(key=lambda x: x[1], reverse=True)

    attack_csv = results_dir / "mapreduce_attack_counts.csv"
    with open(attack_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["attack_type", "event_count", "percentage"])
        total_evs = sum(count for _, count in attack_records)
        for atk, count in attack_records:
            pct = (count / total_evs * 100) if total_evs > 0 else 0
            writer.writerow([atk, count, f"{pct:.2f}%"])

    logger.info(f"Saved MapReduce summary CSVs to {results_dir}")
    return summary
