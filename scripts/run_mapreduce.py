"""CLI script to execute Hadoop MapReduce analytics jobs."""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.logger import get_logger
from src.common.utils import get_project_root
from src.mapreduce.run_mapreduce import run_all_mapreduce_jobs

logger = get_logger("mapreduce_cli")


def parse_args():
    parser = argparse.ArgumentParser(description="Execute Hadoop MapReduce distributed batch processing.")
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Input CSV dataset file. Defaults to HDFS staged file or data/generated/events_10000.csv"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="results/mapreduce",
        help="Directory to store MapReduce job output files."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = get_project_root()

    if args.input:
        input_path = (root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    else:
        # Check HDFS staged file first, then local generated
        emulated_staged = root / "data" / "hdfs_emulated" / "cyber-threat" / "raw" / "events_10000.csv"
        generated_local = root / "data" / "generated" / "events_10000.csv"
        sample_local = root / "data" / "samples" / "sample_events.csv"

        if emulated_staged.exists():
            input_path = emulated_staged
        elif generated_local.exists():
            input_path = generated_local
        elif sample_local.exists():
            input_path = sample_local
        else:
            logger.error("No input dataset found. Run scripts/generate_data.py first.")
            sys.exit(1)

    results_dir = (root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)

    print("\n=======================================================")
    print("      HADOOP MAPREDUCE DISTRIBUTED ANALYTICS BATCH     ")
    print("=======================================================")
    print(f"Input Dataset:      {input_path}")
    print(f"Results Directory:  {results_dir}\n")

    summary = run_all_mapreduce_jobs(input_path, results_dir)

    print("\n--- MAPREDUCE EXECUTION RESULTS ---")
    for job_key, stats in summary.items():
        print(f"[{stats['job_type'].upper():<20}] -> Records: {stats['output_records']:<6} in {stats['elapsed_seconds']:.3f}s")

    print("\nGenerated Output Artifacts:")
    print(f" - {results_dir / 'mapreduce_top_ips.csv'}")
    print(f" - {results_dir / 'mapreduce_attack_counts.csv'}")
    print(f" - {results_dir / 'job1_ip_counts.tsv'}")
    print(f" - {results_dir / 'job2_attack_frequencies.tsv'}")
    print(f" - {results_dir / 'job3_port_activity.tsv'}")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
