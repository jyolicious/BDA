"""CLI script to upload dataset files to HDFS and verify cluster/storage contents."""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common.logger import get_logger
from src.common.utils import get_project_root
from src.hdfs.hdfs_manager import HDFSManager

logger = get_logger("hdfs_upload_cli")


def parse_args():
    parser = argparse.ArgumentParser(description="Upload network telemetry data to HDFS.")
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="data/samples/sample_events.csv",
        help="Local file path to upload into HDFS."
    )
    parser.add_argument(
        "--dest", "-d",
        type=str,
        default="/cyber-threat/raw/",
        help="Target HDFS destination directory or path."
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List HDFS contents of destination directory after upload."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = get_project_root()
    input_path = (root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    manager = HDFSManager()
    manager.setup_directories()

    logger.info(f"Uploading {input_path} to HDFS destination: {args.dest}")
    success = manager.upload(str(input_path), args.dest)

    if success:
        target_name = input_path.name
        verify_path = f"{args.dest.rstrip('/')}/{target_name}"
        status = manager.verify_file(verify_path)
        logger.info(f"Verification status: {status}")

        if args.list:
            items = manager.list_dir(args.dest)
            print(f"\n--- HDFS Directory Listing [{args.dest}] ---")
            for item in items:
                print(f"  {item['type']:<10} {item['length']:>10} bytes  {item['name']}")
            print("-------------------------------------------\n")
    else:
        logger.error("Upload operation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
