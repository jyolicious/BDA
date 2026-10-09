"""Real-time Streaming Network Event Producer.

Generates continuous network telemetry streams with dynamic mode switching
supporting NORMAL, DDOS, PORT_SCAN, and ANOMALY simulation.
"""
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from src.common.logger import get_logger
from src.data.generator import NetworkEventGenerator
from src.data.schema import NetworkEvent

logger = get_logger("event_producer")


class StreamingEventProducer:
    """Continuous network event producer supporting interactive mode switching."""

    DEFAULT_RATES: Dict[str, float] = {
        "NORMAL": 40.0,         # 40 events/sec baseline
        "DDOS": 250.0,          # 250 events/sec volumetric flood
        "PORT_SCAN": 120.0,     # 120 events/sec rapid probing
        "ANOMALY": 60.0         # 60 events/sec irregular telemetry
    }

    def __init__(self, mode: str = "NORMAL", custom_rate: Optional[float] = None):
        self.mode = mode.upper()
        self.generator = NetworkEventGenerator()
        self.custom_rate = custom_rate

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.total_produced = 0
        self.start_time = 0.0

    @property
    def current_rate(self) -> float:
        """Return target events per second for the active mode."""
        if self.custom_rate is not None:
            return self.custom_rate
        return self.DEFAULT_RATES.get(self.mode, 40.0)

    def set_mode(self, new_mode: str) -> None:
        """Dynamically transition stream traffic generation mode."""
        valid_modes = {"NORMAL", "DDOS", "PORT_SCAN", "ANOMALY", "ANOMALOUS"}
        norm = new_mode.upper()
        if norm == "ANOMALOUS":
            norm = "ANOMALY"
        if norm in valid_modes:
            prev = self.mode
            self.mode = norm
            logger.info(f"Stream generation mode switched: {prev} -> {self.mode} (target rate: {self.current_rate:.0f} ev/s)")
        else:
            logger.warning(f"Invalid streaming mode requested: {new_mode}")

    def produce_single_event(self) -> NetworkEvent:
        """Generate next sequential event according to current active mode."""
        # Map ANOMALY -> generator profile ANOMALOUS
        gen_type = "ANOMALOUS" if self.mode == "ANOMALY" else self.mode
        ev = self.generator.generate_single_event(
            traffic_type=gen_type,
            timestamp=datetime.now(timezone.utc)
        )
        self.total_produced += 1
        return ev

    def produce_batch(self, count: int) -> List[NetworkEvent]:
        """Generate a discrete batch of events under current mode."""
        return [self.produce_single_event() for _ in range(count)]

    def start_streaming(self, on_event_callback: Callable[[NetworkEvent], None]) -> None:
        """Start non-blocking background streaming thread."""
        if self._running:
            return

        self._running = True
        self.start_time = time.time()

        def _worker():
            logger.info(f"Event streaming producer started in mode '{self.mode}'.")
            while self._running:
                target_rate = self.current_rate
                sleep_interval = 1.0 / max(target_rate, 1.0)
                batch_size = max(1, int(target_rate // 20))  # Send in micro-bursts of 50ms

                for _ in range(batch_size):
                    if not self._running:
                        break
                    event = self.produce_single_event()
                    on_event_callback(event)

                time.sleep(sleep_interval * batch_size)

            logger.info("Event streaming producer stopped.")

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def stop_streaming(self) -> None:
        """Halt streaming generation thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            self._thread = None

    def get_stats(self) -> Dict[str, Any]:
        """Return operational producer telemetry."""
        uptime = (time.time() - self.start_time) if self._running else 0.0
        effective_rate = (self.total_produced / uptime) if uptime > 0 else 0.0
        return {
            "mode": self.mode,
            "is_running": self._running,
            "target_rate_eps": self.current_rate,
            "total_produced": self.total_produced,
            "uptime_seconds": round(uptime, 1),
            "effective_rate_eps": round(effective_rate, 1)
        }
