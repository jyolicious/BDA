"""Unit tests for sliding window state maintenance and deterministic pruning."""
import pytest
from src.streaming.sliding_window import SlidingWindowTracker
from src.data.generator import NetworkEventGenerator


def test_sliding_window_aggregation():
    tracker = SlidingWindowTracker(window_size_seconds=60.0)
    gen = NetworkEventGenerator(seed=42)

    events = gen.generate_batch(total_events=50)
    for ev in events:
        tracker.add_event(ev, custom_timestamp=100.0)

    hosts = tracker.get_all_active_hosts()
    assert len(hosts) > 0

    first_host = hosts[0]
    metrics = tracker.get_host_metrics(first_host)
    assert metrics is not None
    assert metrics["event_count"] >= 1
    assert metrics["total_bytes"] > 0


def test_sliding_window_pruning():
    tracker = SlidingWindowTracker(window_size_seconds=10.0)
    gen = NetworkEventGenerator(seed=42)

    ev1 = gen.generate_single_event("NORMAL")
    tracker.add_event(ev1, custom_timestamp=10.0)
    assert len(tracker.get_all_active_hosts()) == 1

    # Advance time past 10-second window
    ev2 = gen.generate_single_event("NORMAL")
    tracker.add_event(ev2, custom_timestamp=25.0)

    # ev1 should have been evicted
    assert len(tracker.event_queue) == 1
    assert tracker.event_queue[0][0] == 25.0
