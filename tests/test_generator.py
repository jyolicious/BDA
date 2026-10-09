"""Unit tests for Network Event Generator and Schema validation."""
import pytest
from src.data.generator import NetworkEventGenerator
from src.data.schema import NetworkEvent, EVENT_SCHEMA_FIELDS


def test_schema_serialization():
    ev = NetworkEvent(
        timestamp="2026-10-09T00:01:23",
        source_ip="192.168.1.25",
        destination_ip="10.0.0.15",
        source_port=45321,
        destination_port=443,
        protocol="TCP",
        packet_count=42,
        bytes_sent=5280,
        bytes_received=42100,
        duration_ms=152,
        connection_status="SUCCESS",
        attack_label="NORMAL"
    )

    assert ev.validate() is True
    csv_row = ev.to_csv_row()
    reconstructed = NetworkEvent.from_csv_line(csv_row)
    assert reconstructed.source_ip == ev.source_ip
    assert reconstructed.bytes_sent == ev.bytes_sent
    assert reconstructed.destination_port == ev.destination_port


def test_generator_single_events():
    gen = NetworkEventGenerator(seed=123)

    for profile in ["NORMAL", "DDOS", "PORT_SCAN", "ANOMALOUS"]:
        ev = gen.generate_single_event(traffic_type=profile)
        assert ev.validate() is True
        assert ev.attack_label in {"NORMAL", "DDOS", "PORT_SCAN", "ANOMALOUS"}


def test_generator_batch():
    gen = NetworkEventGenerator(seed=42)
    batch = gen.generate_batch(total_events=500)
    assert len(batch) == 500
    labels = {ev.attack_label for ev in batch}
    assert "NORMAL" in labels
    assert "DDOS" in labels
