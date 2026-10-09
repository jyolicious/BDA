@echo off
REM ==============================================================================
REM HDFS Directory Setup Script (Windows)
REM Creates the logical /cyber-threat directories in HDFS or Emulated Storage
REM ==============================================================================

echo [HDFS SETUP] Initializing Cyber Threat HDFS Logical Directories...
python -c "from src.hdfs.hdfs_manager import HDFSManager; m = HDFSManager(); m.setup_directories(); print('[HDFS SETUP] Complete. Mode: Native' if m.is_native_active else '[HDFS SETUP] Complete. Mode: Emulated HDFS')"
pause
