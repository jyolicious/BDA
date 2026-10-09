#!/usr/bin/env bash
# ==============================================================================
# HDFS Directory Setup Script (Linux/Mac/WSL)
# ==============================================================================

echo "[HDFS SETUP] Initializing Cyber Threat HDFS Logical Directories..."
python3 -c "from src.hdfs.hdfs_manager import HDFSManager; m = HDFSManager(); m.setup_directories(); print('[HDFS SETUP] Complete. Mode: Native' if m.is_native_active else '[HDFS SETUP] Complete. Mode: Emulated HDFS')"
