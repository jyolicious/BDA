"""Synthetic Network Event Generator.

Generates realistic network telemetry supporting:
- NORMAL traffic patterns
- DDOS volumetric floods
- PORT_SCAN reconnaissance sweeps
- ANOMALOUS asymmetric/covert channel events
"""
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Generator, List, Optional
from src.data.schema import NetworkEvent


class NetworkEventGenerator:
    """Configurable synthetic network telemetry generator."""

    COMMON_PORTS = [80, 443, 53, 22, 8080, 8443, 25, 123, 389, 636]
    SCAN_PORT_RANGE = list(range(20, 1025)) + [1433, 3306, 3389, 5432, 8000, 8080, 8888]
    ANOMALOUS_PORTS = [4444, 6667, 1337, 31337, 9999, 12345, 5555, 27017, 9092]
    PROTOCOLS = ["TCP", "UDP", "ICMP"]

    def __init__(
        self,
        seed: Optional[int] = 42,
        target_servers: Optional[List[str]] = None,
        ddos_attackers: Optional[List[str]] = None,
        scanner_ips: Optional[List[str]] = None,
        normal_pool_size: int = 200,
    ):
        if seed is not None:
            random.seed(seed)

        self.target_servers = target_servers or [
            "10.0.0.5", "10.0.0.10", "10.0.0.15", "10.0.0.20", "10.0.0.25"
        ]
        self.ddos_attackers = ddos_attackers or [
            "185.220.101.5", "185.220.101.9", "194.26.29.11", "45.154.255.88", "198.51.100.42"
        ]
        self.scanner_ips = scanner_ips or [
            "198.18.0.15", "198.18.0.42", "203.0.113.77", "192.0.2.99"
        ]
        self.anomalous_ips = [
            "172.16.50.12", "172.16.50.89", "172.16.50.210"
        ]

        # Generate pool of normal internal/external client IPs
        self.normal_ips = [
            f"192.168.1.{i}" for i in range(10, min(10 + normal_pool_size, 250))
        ] + [
            f"172.20.14.{i}" for i in range(2, 60)
        ]

    def generate_single_event(
        self,
        traffic_type: str = "NORMAL",
        timestamp: Optional[datetime] = None,
        source_ip: Optional[str] = None,
        dest_ip: Optional[str] = None
    ) -> NetworkEvent:
        """Generate a single network event adhering to traffic behavioral profile."""
        ts_str = (timestamp or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%S")

        if traffic_type == "DDOS":
            src_ip = source_ip or random.choice(self.ddos_attackers)
            dst_ip = dest_ip or self.target_servers[0]  # Concentrate on high-value target
            dst_port = random.choice([80, 443, 8080])
            protocol = random.choice(["TCP", "UDP"])
            packet_count = random.randint(250, 4500)
            bytes_sent = random.randint(120000, 950000)
            bytes_received = random.randint(100, 2500)
            duration_ms = random.randint(2, 25)
            status = random.choices(["SUCCESS", "TIMEOUT", "FAILED"], weights=[0.4, 0.4, 0.2])[0]
            label = "DDOS"

        elif traffic_type == "PORT_SCAN":
            src_ip = source_ip or random.choice(self.scanner_ips)
            dst_ip = dest_ip or random.choice(self.target_servers)
            dst_port = random.choice(self.SCAN_PORT_RANGE)
            protocol = "TCP"
            packet_count = random.randint(1, 4)
            bytes_sent = random.randint(40, 180)
            bytes_received = random.randint(0, 40)
            duration_ms = random.randint(1, 20)
            status = random.choices(["REJECTED", "FAILED", "TIMEOUT", "SUCCESS"], weights=[0.60, 0.25, 0.10, 0.05])[0]
            label = "PORT_SCAN"

        elif traffic_type == "ANOMALOUS":
            src_ip = source_ip or random.choice(self.anomalous_ips)
            dst_ip = dest_ip or random.choice(self.target_servers)
            dst_port = random.choice(self.ANOMALOUS_PORTS)
            protocol = random.choice(["TCP", "UDP"])
            # Massive exfiltration asymmetry: heavy sent bytes, minimal received bytes
            packet_count = random.randint(150, 1200)
            bytes_sent = random.randint(400000, 2500000)
            bytes_received = random.randint(100, 1500)
            duration_ms = random.randint(300, 3500)
            status = random.choices(["SUCCESS", "TIMEOUT"], weights=[0.8, 0.2])[0]
            label = "ANOMALOUS"

        else:  # NORMAL
            src_ip = source_ip or random.choice(self.normal_ips)
            dst_ip = dest_ip or random.choice(self.target_servers)
            dst_port = random.choice(self.COMMON_PORTS)
            protocol = random.choices(["TCP", "UDP", "ICMP"], weights=[0.8, 0.18, 0.02])[0]
            packet_count = random.randint(4, 85)
            bytes_sent = random.randint(450, 18000)
            bytes_received = random.randint(1200, 65000)
            duration_ms = random.randint(35, 450)
            status = random.choices(["SUCCESS", "FAILED", "TIMEOUT"], weights=[0.95, 0.04, 0.01])[0]
            label = "NORMAL"

        return NetworkEvent(
            timestamp=ts_str,
            source_ip=src_ip,
            destination_ip=dst_ip,
            source_port=random.randint(1024, 65535),
            destination_port=dst_port,
            protocol=protocol,
            packet_count=packet_count,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            duration_ms=duration_ms,
            connection_status=status,
            attack_label=label
        )

    def generate_batch(
        self,
        total_events: int = 10000,
        distribution: Optional[Dict[str, float]] = None,
        start_time: Optional[datetime] = None,
        duration_hours: float = 2.0
    ) -> List[NetworkEvent]:
        """Generate a list of network events over a simulated time window."""
        dist = distribution or {
            "NORMAL": 0.70,
            "DDOS": 0.10,
            "PORT_SCAN": 0.10,
            "ANOMALOUS": 0.10
        }
        types = list(dist.keys())
        weights = list(dist.values())

        base_time = start_time or (datetime.now(timezone.utc) - timedelta(hours=duration_hours))
        sec_step = (duration_hours * 3600.0) / max(total_events, 1)

        events: List[NetworkEvent] = []
        for i in range(total_events):
            t_offset = timedelta(seconds=i * sec_step + random.uniform(0, sec_step))
            ev_time = base_time + t_offset
            chosen_type = random.choices(types, weights=weights)[0]
            events.append(self.generate_single_event(chosen_type, timestamp=ev_time))

        return events

    def stream_events(
        self,
        mode: str = "NORMAL",
        count: Optional[int] = None
    ) -> Generator[NetworkEvent, None, None]:
        """Generator yielding infinite or bounded stream events of a given profile."""
        generated = 0
        while count is None or generated < count:
            yield self.generate_single_event(traffic_type=mode.upper())
            generated += 1
