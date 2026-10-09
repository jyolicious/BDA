"""Shared helper utilities for project configuration and path management."""
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

def get_project_root() -> Path:
    """Return the absolute Path to the root directory of the project."""
    # This file is in src/common/utils.py -> 2 levels up is project root
    return Path(__file__).resolve().parent.parent.parent

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load config/config.yaml with environment override support."""
    root = get_project_root()
    path = Path(config_path) if config_path else root / "config" / "config.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Optional environment variable overrides
    if "MONGO_URI" in os.environ:
        config["database"]["mongo_uri"] = os.environ["MONGO_URI"]
    if "HDFS_URL" in os.environ:
        config["hdfs"]["webhdfs_url"] = os.environ["HDFS_URL"]

    return config

def load_detection_rules(rules_path: Optional[str] = None) -> Dict[str, Any]:
    """Load config/detection_rules.yaml."""
    root = get_project_root()
    path = Path(rules_path) if rules_path else root / "config" / "detection_rules.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Detection rules file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_directories(dirs: List[Path]) -> None:
    """Ensure that all provided directory paths exist."""
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

def current_utc_iso() -> str:
    """Return current UTC timestamp in ISO 8601 string format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

def parse_iso_timestamp(ts_str: str) -> datetime:
    """Parse ISO 8601 string to datetime object."""
    # Handles both 'Z' and offset or standard formats
    cleaned = ts_str.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except Exception:
        return datetime.strptime(ts_str[:19], "%Y-%m-%dT%H:%M:%S")
