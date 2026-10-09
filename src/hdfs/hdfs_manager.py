"""HDFS Management Module.

Provides robust HDFS operations for:
- Logical directory provisioning (/cyber-threat/raw, /cyber-threat/processed, etc.)
- Uploading and staging raw network event batches
- Listing, inspecting, and retrieving distributed datasets
- Real-time fallback to structured local emulated HDFS storage when Hadoop daemons are offline.
"""
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.common.logger import get_logger
from src.common.utils import get_project_root, load_config

logger = get_logger("hdfs_manager")


class HDFSManager:
    """Manages HDFS interaction using WebHDFS or local structured storage."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_config()
        hdfs_conf = self.config.get("hdfs", {})
        self.webhdfs_url = hdfs_conf.get("webhdfs_url", "http://localhost:9870")
        self.user = hdfs_conf.get("user", "hadoop")
        self.allow_fallback = hdfs_conf.get("allow_emulated_fallback", True)

        root = get_project_root()
        emulated_rel = hdfs_conf.get("emulated_dir", "data/hdfs_emulated")
        self.emulated_base = (root / emulated_rel).resolve()

        self.native_client = None
        self.is_native_active = False

        self._init_connection()

    def _init_connection(self) -> None:
        """Attempt connection to native WebHDFS cluster."""
        try:
            from hdfs import InsecureClient
            client = InsecureClient(self.webhdfs_url, user=self.user, timeout=3)
            # Test connectivity by listing root
            client.list("/")
            self.native_client = client
            self.is_native_active = True
            logger.info(f"[HDFS MODE: NATIVE] Connected to WebHDFS cluster at {self.webhdfs_url} as {self.user}")
        except Exception as ex:
            self.is_native_active = False
            self.native_client = None
            if self.allow_fallback:
                logger.warning(
                    f"[HDFS MODE: EMULATED FALLBACK] Native HDFS cluster not responding at {self.webhdfs_url} ({ex}). "
                    f"Operating in verified local HDFS-emulated filesystem at '{self.emulated_base}'."
                )
            else:
                logger.error(
                    f"CRITICAL: Failed to connect to native HDFS at {self.webhdfs_url}. "
                    "Ensure NameNode and DataNode daemons are running or enable 'allow_emulated_fallback'."
                )

    def _to_emulated_path(self, hdfs_path: str) -> Path:
        """Map logical HDFS path e.g. /cyber-threat/raw to local emulated folder."""
        clean = hdfs_path.lstrip("/").replace("/", os.sep)
        return self.emulated_base / clean

    def mkdir(self, hdfs_path: str) -> bool:
        """Create a logical directory in HDFS."""
        if self.is_native_active:
            try:
                self.native_client.makedirs(hdfs_path)
                logger.info(f"[NATIVE HDFS] Created directory: {hdfs_path}")
                return True
            except Exception as e:
                logger.error(f"[NATIVE HDFS] Failed to create directory {hdfs_path}: {e}")
                return False
        else:
            local_target = self._to_emulated_path(hdfs_path)
            local_target.mkdir(parents=True, exist_ok=True)
            logger.info(f"[EMULATED HDFS] Created logical directory: {hdfs_path} -> {local_target}")
            return True

    def setup_directories(self) -> None:
        """Create standard pipeline directories."""
        dirs = self.config.get("hdfs", {}).get("directories", {})
        for name, path in dirs.items():
            self.mkdir(path)

    def upload(self, local_path: str, hdfs_path: str, overwrite: bool = True) -> bool:
        """Upload a local dataset file into HDFS target location."""
        src = Path(local_path).resolve()
        if not src.exists():
            raise FileNotFoundError(f"Local source file not found: {src}")

        if self.is_native_active:
            try:
                self.native_client.upload(hdfs_path, str(src), overwrite=overwrite)
                logger.info(f"[NATIVE HDFS] Uploaded {src.name} to {hdfs_path}")
                return True
            except Exception as e:
                logger.error(f"[NATIVE HDFS] Upload failed for {src}: {e}")
                return False
        else:
            dst = self._to_emulated_path(hdfs_path)
            if dst.is_dir() or hdfs_path.endswith("/"):
                dst.mkdir(parents=True, exist_ok=True)
                dst = dst / src.name
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(str(src), str(dst))
            logger.info(f"[EMULATED HDFS] Staged {src.name} ({src.stat().st_size:,} bytes) into HDFS path {hdfs_path} -> {dst}")
            return True

    def list_dir(self, hdfs_path: str) -> List[Dict[str, Any]]:
        """List contents and metadata of an HDFS directory."""
        if self.is_native_active:
            try:
                entries = self.native_client.list(hdfs_path, status=True)
                results = []
                for name, status in entries:
                    results.append({
                        "name": name,
                        "type": status["type"],
                        "length": status["length"],
                        "path": f"{hdfs_path.rstrip('/')}/{name}"
                    })
                return results
            except Exception as e:
                logger.error(f"[NATIVE HDFS] List failed for {hdfs_path}: {e}")
                return []
        else:
            local_dir = self._to_emulated_path(hdfs_path)
            if not local_dir.exists():
                logger.warning(f"[EMULATED HDFS] Directory does not exist: {local_dir}")
                return []

            results = []
            for item in local_dir.iterdir():
                results.append({
                    "name": item.name,
                    "type": "DIRECTORY" if item.is_dir() else "FILE",
                    "length": item.stat().st_size if item.is_file() else 0,
                    "path": f"{hdfs_path.rstrip('/')}/{item.name}",
                    "local_resolved_path": str(item)
                })
            return results

    def verify_file(self, hdfs_path: str) -> Dict[str, Any]:
        """Verify file existence, size, and readiness in HDFS."""
        if self.is_native_active:
            try:
                status = self.native_client.status(hdfs_path)
                return {
                    "exists": True,
                    "length": status["length"],
                    "type": status["type"],
                    "owner": status["owner"],
                    "path": hdfs_path
                }
            except Exception as e:
                return {"exists": False, "error": str(e), "path": hdfs_path}
        else:
            local_path = self._to_emulated_path(hdfs_path)
            if local_path.exists():
                return {
                    "exists": True,
                    "length": local_path.stat().st_size if local_path.is_file() else 0,
                    "type": "FILE" if local_path.is_file() else "DIRECTORY",
                    "path": hdfs_path,
                    "local_resolved_path": str(local_path)
                }
            return {"exists": False, "error": "Path does not exist", "path": hdfs_path}

    def download(self, hdfs_path: str, local_path: str, overwrite: bool = True) -> bool:
        """Download a file from HDFS to local path."""
        target = Path(local_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)

        if self.is_native_active:
            try:
                self.native_client.download(hdfs_path, str(target), overwrite=overwrite)
                logger.info(f"[NATIVE HDFS] Downloaded {hdfs_path} to {target}")
                return True
            except Exception as e:
                logger.error(f"[NATIVE HDFS] Download failed for {hdfs_path}: {e}")
                return False
        else:
            src = self._to_emulated_path(hdfs_path)
            if not src.exists():
                logger.error(f"[EMULATED HDFS] Source path {src} not found")
                return False
            shutil.copy2(str(src), str(target))
            logger.info(f"[EMULATED HDFS] Retrieved {hdfs_path} -> {target}")
            return True

    def get_actual_read_path(self, hdfs_path: str) -> str:
        """Return URI or filesystem path suitable for Spark/Hadoop reading."""
        if self.is_native_active:
            return f"hdfs://localhost:9000{hdfs_path}"
        else:
            return str(self._to_emulated_path(hdfs_path))
