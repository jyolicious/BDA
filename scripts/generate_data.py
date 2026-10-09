"""CLI Script to generate synthetic network event datasets for big data analytics."""
import argparse
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.logger import get_logger
from src.common.utils import get_project_root, load_config
from src.data.generator import NetworkEventGenerator
from src.data.dataset_loader import DatasetLoader
from src.data.schema import EVENT_SCHEMA_FIELDS

logger = get_logger("data_generator")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate synthetic network event datasets for Big Data analytics."
    )
    parser.add_argument(
        "--events", "-n",
        type=int,
        default=10000,
        help="Number of network events to generate (e.g. 10000, 100000, 1000000)."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Target output CSV file path. Defaults to data/generated/events_<N>.csv"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed for reproducibility."
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=50000,
        help="Batch write chunk size to minimize memory consumption."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = get_project_root()
    config = load_config()

    total_events = args.events
    out_path = Path(args.output) if args.output else root / "data" / "generated" / f"events_{total_events}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating {total_events:,} synthetic network events...")
    logger.info(f"Output path: {out_path}")
    logger.info(f"Random seed: {args.seed}")

    generator = NetworkEventGenerator(seed=args.seed)

    # Write events incrementally to handle arbitrary sizes (10k up to 10M+)
    written = 0
    chunk_size = min(args.chunk_size, total_events)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        # Write schema header
        f.write(",".join(EVENT_SCHEMA_FIELDS) + "\n")

        while written < total_events:
            current_batch_size = min(chunk_size, total_events - written)
            batch = generator.generate_batch(total_events=current_batch_size)
            for ev in batch:
                f.write(ev.to_csv_row() + "\n")
            written += current_batch_size
            if written % max(50000, chunk_size) == 0 or written == total_events:
                logger.info(f"Progress: {written:,} / {total_events:,} events written ({written/total_events*100:.1f}%)")

    file_size_mb = out_path.stat().st_size / (1024 * 1024)
    logger.info(f"Successfully generated {written:,} events.")
    logger.info(f"File size on disk: {file_size_mb:.2f} MB at {out_path}")

    # Also create a small sample in data/samples/sample_events.csv if it doesn't exist
    sample_path = root / "data" / "samples" / "sample_events.csv"
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    if not sample_path.exists() or sample_path.stat().st_size == 0:
        logger.info(f"Creating sample events preview at {sample_path} (1,000 events)...")
        sample_batch = generator.generate_batch(total_events=1000)
        DatasetLoader.save_csv(sample_batch, sample_path)

    print("\n--- GENERATION SUMMARY ---")
    print(f"Total events:  {written:,}")
    print(f"Target file:   {out_path}")
    print(f"File size:     {file_size_mb:.2f} MB")
    print("---------------------------\n")


if __name__ == "__main__":
    main()
