"""SparkSession lifecycle and environment initialization."""
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from pyspark.sql import SparkSession
from src.common.logger import get_logger
from src.common.utils import load_config

logger = get_logger("spark_session")


def get_spark_session(config: Optional[Dict[str, Any]] = None) -> SparkSession:
    """Initialize and return a production-configured SparkSession."""
    cfg = config or load_config()
    spark_cfg = cfg.get("spark", {})

    # Ensure Python runtime matches the current environment
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    # Check for local winutils/Hadoop
    if "HADOOP_HOME" not in os.environ:
        if Path("C:/hadoop").exists():
            os.environ["HADOOP_HOME"] = "C:/hadoop"

    app_name = spark_cfg.get("app_name", "CyberThreatIntelligence_Spark")
    master = spark_cfg.get("master", "local[*]")
    driver_mem = spark_cfg.get("driver_memory", "4g")
    shuffle_parts = str(spark_cfg.get("sql_shuffle_partitions", 8))

    logger.info(f"Initializing SparkSession: app='{app_name}', master='{master}'...")

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.driver.memory", driver_mem)
        .config("spark.sql.shuffle.partitions", shuffle_parts)
        .config("spark.sql.execution.arrow.pyspark.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
    )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    logger.info(f"SparkSession ready (Spark version: {spark.version}).")
    return spark


def stop_spark_session(spark: SparkSession) -> None:
    """Safely terminate SparkContext and release compute resources."""
    if spark:
        try:
            spark.stop()
            logger.info("SparkSession stopped successfully.")
        except Exception as e:
            logger.warning(f"Error stopping SparkSession: {e}")
