"""End-to-End Smoke Test for the Streaming Threat Intelligence Pipeline."""
import pytest
from src.data.generator import NetworkEventGenerator
from src.streaming.pipeline import StreamingPipeline
from src.database.mongodb import MongoDBManager


def test_pipeline_smoke_run():
    """Execute rapid end-to-end smoke test across 1,000 synthetic events."""
    generator = NetworkEventGenerator(seed=99)
    events = generator.generate_batch(total_events=1000)

    alerts_captured = []

    def on_alert_detected(alert):
        alerts_captured.append(alert)

    db = MongoDBManager()
    pipeline = StreamingPipeline(db_manager=db, on_alert_callback=on_alert_detected)

    for ev in events:
        pipeline.process_event(ev)

    tel = pipeline.get_pipeline_telemetry()

    assert tel["events_processed"] == 1000
    assert tel["active_window_events"] > 0
    assert tel["bloom_filter"]["elements_added"] == 1000
    # Smoke test confirms threats are identified
    assert tel["threats_detected"] > 0
