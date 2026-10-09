"""Canonical Network Event Schema definition.

Enforces unified event structure across CSV files, Hadoop MapReduce,
Spark DataFrames, streaming pipelines, and MongoDB documents.
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import json

EVENT_SCHEMA_FIELDS: List[str] = [
    "timestamp",
    "source_ip",
    "destination_ip",
    "source_port",
    "destination_port",
    "protocol",
    "packet_count",
    "bytes_sent",
    "bytes_received",
    "duration_ms",
    "connection_status",
    "attack_label"
]

VALID_PROTOCOLS = {"TCP", "UDP", "ICMP"}
VALID_STATUSES = {"SUCCESS", "FAILED", "TIMEOUT", "REJECTED"}
VALID_ATTACK_LABELS = {"NORMAL", "DDOS", "PORT_SCAN", "ANOMALOUS"}


@dataclass
class NetworkEvent:
    """Represents an atomic network telemetry event record."""
    timestamp: str            # ISO 8601 format UTC, e.g. '2026-10-09T00:01:23'
    source_ip: str            # IPv4 address, e.g. '192.168.1.25'
    destination_ip: str       # IPv4 address, e.g. '10.0.0.15'
    source_port: int          # 1024 - 65535
    destination_port: int     # 1 - 65535
    protocol: str             # TCP, UDP, ICMP
    packet_count: int         # Total packets exchanged in flow
    bytes_sent: int           # Raw payload + header bytes transmitted
    bytes_received: int       # Raw bytes received in response
    duration_ms: int          # Flow connection duration in milliseconds
    connection_status: str    # SUCCESS, FAILED, TIMEOUT, REJECTED
    attack_label: str         # NORMAL, DDOS, PORT_SCAN, ANOMALOUS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary matching MongoDB and JSON formatting."""
        return asdict(self)

    def to_csv_row(self) -> str:
        """Format as comma-delimited string matching standard CSV headers."""
        return (
            f"{self.timestamp},{self.source_ip},{self.destination_ip},"
            f"{self.source_port},{self.destination_port},{self.protocol},"
            f"{self.packet_count},{self.bytes_sent},{self.bytes_received},"
            f"{self.duration_ms},{self.connection_status},{self.attack_label}"
        )

    def to_tuple(self) -> tuple:
        """Return tuple of ordered fields for dataframe conversion."""
        return (
            self.timestamp,
            self.source_ip,
            self.destination_ip,
            int(self.source_port),
            int(self.destination_port),
            str(self.protocol),
            int(self.packet_count),
            int(self.bytes_sent),
            int(self.bytes_received),
            int(self.duration_ms),
            str(self.connection_status),
            str(self.attack_label)
        )

    def to_json(self) -> str:
        """Serialize event to compact JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NetworkEvent":
        """Reconstruct event object from key-value dictionary."""
        return cls(
            timestamp=str(data["timestamp"]),
            source_ip=str(data["source_ip"]),
            destination_ip=str(data["destination_ip"]),
            source_port=int(data["source_port"]),
            destination_port=int(data["destination_port"]),
            protocol=str(data["protocol"]),
            packet_count=int(data["packet_count"]),
            bytes_sent=int(data["bytes_sent"]),
            bytes_received=int(data["bytes_received"]),
            duration_ms=int(data["duration_ms"]),
            connection_status=str(data["connection_status"]),
            attack_label=str(data["attack_label"])
        )

    @classmethod
    def from_csv_line(cls, line: str) -> "NetworkEvent":
        """Parse raw CSV row string into NetworkEvent instance."""
        parts = line.strip().split(",")
        if len(parts) != 12:
            raise ValueError(f"Malformed event line, expected 12 fields, got {len(parts)}: {line}")
        return cls(
            timestamp=parts[0],
            source_ip=parts[1],
            destination_ip=parts[2],
            source_port=int(parts[3]),
            destination_port=int(parts[4]),
            protocol=parts[5],
            packet_count=int(parts[6]),
            bytes_sent=int(parts[7]),
            bytes_received=int(parts[8]),
            duration_ms=int(parts[9]),
            connection_status=parts[10],
            attack_label=parts[11]
        )

    def validate(self) -> bool:
        """Sanity check event attributes."""
        if self.protocol not in VALID_PROTOCOLS:
            return False
        if self.connection_status not in VALID_STATUSES:
            return False
        if self.attack_label not in VALID_ATTACK_LABELS:
            return False
        if self.packet_count < 0 or self.bytes_sent < 0 or self.bytes_received < 0:
            return False
        return True


def get_spark_schema():
    """Return PySpark StructType schema matching NetworkEvent."""
    from pyspark.sql.types import (
        StructType, StructField, StringType, IntegerType, LongType
    )
    return StructType([
        StructField("timestamp", StringType(), False),
        StructField("source_ip", StringType(), False),
        StructField("destination_ip", StringType(), False),
        StructField("source_port", IntegerType(), False),
        StructField("destination_port", IntegerType(), False),
        StructField("protocol", StringType(), False),
        StructField("packet_count", IntegerType(), False),
        StructField("bytes_sent", LongType(), False),
        StructField("bytes_received", LongType(), False),
        StructField("duration_ms", IntegerType(), False),
        StructField("connection_status", StringType(), False),
        StructField("attack_label", StringType(), False),
    ])
