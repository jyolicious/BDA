"""Sliding Window State Tracker for Real-Time Streaming Analytics.

Maintains fine-grained rolling state over a configurable time window (default 5 minutes).
Prunes expired event telemetry deterministically as stream time advances.
"""
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from src.data.schema import NetworkEvent


class HostWindowStats:
    """Maintains active window statistics for an individual source IP."""
    __slots__ = (
        "ip", "event_count", "bytes_sent", "bytes_received",
        "packet_count", "failed_conn_count", "port_counts",
        "first_seen", "last_seen"
    )

    def __init__(self, ip: str, timestamp: float):
        self.ip = ip
        self.event_count = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.packet_count = 0
        self.failed_conn_count = 0
        self.port_counts: Dict[int, int] = defaultdict(int)
        self.first_seen = timestamp
        self.last_seen = timestamp

    def add(self, ev: NetworkEvent, ts: float) -> None:
        self.event_count += 1
        self.bytes_sent += ev.bytes_sent
        self.bytes_received += ev.bytes_received
        self.packet_count += ev.packet_count
        if ev.connection_status in {"FAILED", "REJECTED", "TIMEOUT"}:
            self.failed_conn_count += 1
        self.port_counts[ev.destination_port] += 1
        self.last_seen = max(self.last_seen, ts)
        self.first_seen = min(self.first_seen, ts)

    def remove(self, ev: NetworkEvent) -> None:
        self.event_count -= 1
        self.bytes_sent -= ev.bytes_sent
        self.bytes_received -= ev.bytes_received
        self.packet_count -= ev.packet_count
        if ev.connection_status in {"FAILED", "REJECTED", "TIMEOUT"}:
            self.failed_conn_count -= 1

        p = ev.destination_port
        self.port_counts[p] -= 1
        if self.port_counts[p] <= 0:
            del self.port_counts[p]

    @property
    def unique_ports_count(self) -> int:
        return len(self.port_counts)


class SlidingWindowTracker:
    """Deterministic sliding window manager for streaming network event evaluation."""

    def __init__(self, window_size_seconds: float = 300.0):
        self.window_size_seconds = float(window_size_seconds)
        # deque of (timestamp_float, event)
        self.event_queue: deque = deque()
        # source_ip -> HostWindowStats
        self.hosts: Dict[str, HostWindowStats] = {}
        self.current_window_time: float = 0.0

    @staticmethod
    def _parse_ts(ts_str: str) -> float:
        """Parse event ISO string to Unix timestamp float."""
        try:
            cleaned = ts_str.replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned).timestamp()
        except Exception:
            # Fallback to current time if parsing fails
            return datetime.now(timezone.utc).timestamp()

    def add_event(self, event: NetworkEvent, custom_timestamp: Optional[float] = None) -> None:
        """Ingest event into sliding window and prune out-of-window records."""
        ts = custom_timestamp if custom_timestamp is not None else self._parse_ts(event.timestamp)
        self.current_window_time = max(self.current_window_time, ts)

        # Append to time-ordered deque
        self.event_queue.append((ts, event))

        # Update host stats
        ip = event.source_ip
        if ip not in self.hosts:
            self.hosts[ip] = HostWindowStats(ip, ts)
        self.hosts[ip].add(event, ts)

        # Evict expired events
        self.prune(self.current_window_time)

    def prune(self, current_time: float) -> int:
        """Remove events older than (current_time - window_size_seconds)."""
        cutoff = current_time - self.window_size_seconds
        evicted = 0

        while self.event_queue and self.event_queue[0][0] < cutoff:
            old_ts, old_event = self.event_queue.popleft()
            ip = old_event.source_ip
            if ip in self.hosts:
                self.hosts[ip].remove(old_event)
                if self.hosts[ip].event_count <= 0:
                    del self.hosts[ip]
            evicted += 1

        return evicted

    def get_host_metrics(self, ip: str) -> Optional[Dict[str, Any]]:
        """Compute rate and volume metrics for an IP within the active window."""
        host = self.hosts.get(ip)
        if not host or host.event_count == 0:
            return None

        # Active time span in window
        duration = max(host.last_seen - host.first_seen, 1.0)
        event_rate = host.event_count / duration
        byte_rate = (host.bytes_sent + host.bytes_received) / duration
        packet_rate = host.packet_count / duration
        failed_ratio = (host.failed_conn_count / host.event_count) if host.event_count > 0 else 0.0

        return {
            "source_ip": ip,
            "event_count": host.event_count,
            "bytes_sent": host.bytes_sent,
            "bytes_received": host.bytes_received,
            "total_bytes": host.bytes_sent + host.bytes_received,
            "packet_count": host.packet_count,
            "unique_dest_ports": host.unique_ports_count,
            "failed_connections": host.failed_conn_count,
            "failed_ratio": round(failed_ratio, 4),
            "window_duration_sec": round(duration, 2),
            "event_rate_per_sec": round(event_rate, 2),
            "byte_rate_per_sec": round(byte_rate, 2),
            "packet_rate_per_sec": round(packet_rate, 2),
            "first_seen": host.first_seen,
            "last_seen": host.last_seen
        }

    def get_all_active_hosts(self) -> List[str]:
        """Return list of all source IPs currently having events in the window."""
        return list(self.hosts.keys())

    def get_window_stats(self) -> Dict[str, Any]:
        """Return summary metrics of active sliding window."""
        return {
            "window_size_seconds": self.window_size_seconds,
            "active_events_in_window": len(self.event_queue),
            "active_unique_ips": len(self.hosts),
            "window_head_timestamp": self.event_queue[0][0] if self.event_queue else 0.0,
            "window_tail_timestamp": self.current_window_time
        }
