"""Spark dataset ingestion and schema preprocessing."""
from pathlib import Path
from typing import Union
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col
from src.common.logger import get_logger
from src.data.schema import get_spark_schema

logger = get_logger("spark_preprocessing")


def load_network_events(
    spark: SparkSession,
    dataset_path: Union[str, Path]
) -> DataFrame:
    """Load and validate network telemetry CSV into a typed Spark DataFrame."""
    path_str = str(dataset_path)
    logger.info(f"Loading network event telemetry from: {path_str}")

    schema = get_spark_schema()
    df = (
        spark.read
        .option("header", "true")
        .schema(schema)
        .csv(path_str)
    )

    count = df.count()
    logger.info(f"Loaded {count:,} network events into Spark DataFrame.")
    return df
