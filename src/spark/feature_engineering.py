"""Spark MLlib Feature Engineering Pipeline."""
from typing import List, Tuple
from pyspark.ml.feature import StandardScaler, StandardScalerModel, VectorAssembler
from pyspark.sql import DataFrame
from src.common.logger import get_logger

logger = get_logger("spark_features")

DEFAULT_FEATURE_COLS = [
    "event_count",
    "total_bytes_sent",
    "total_bytes_received",
    "avg_packet_count",
    "unique_dest_ports",
    "failed_conn_count",
    "avg_duration_ms",
    "protocol_diversity"
]


def build_feature_pipeline(
    df: DataFrame,
    feature_cols: List[str] = DEFAULT_FEATURE_COLS,
    scale_features: bool = True
) -> Tuple[DataFrame, StandardScalerModel]:
    """Assemble and scale numerical feature vectors for Spark MLlib algorithms."""
    logger.info(f"Assembling feature vector with columns: {feature_cols}")

    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="raw_features",
        handleInvalid="skip"
    )
    assembled_df = assembler.transform(df)

    if scale_features:
        logger.info("Applying StandardScaler (withMean=True, withStd=True)...")
        scaler = StandardScaler(
            inputCol="raw_features",
            outputCol="features",
            withMean=True,
            withStd=True
        )
        scaler_model = scaler.fit(assembled_df)
        scaled_df = scaler_model.transform(assembled_df)
        return scaled_df, scaler_model
    else:
        assembled_df = assembled_df.withColumnRenamed("raw_features", "features")
        return assembled_df, None
