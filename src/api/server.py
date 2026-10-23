"""FastAPI REST and WebSocket Backend for SENTINEL Cyber Threat Intelligence SOC.

Exposes high-frequency streaming WebSocket telemetry, simulation controls,
historical big data analytics (HDFS, MapReduce, Spark), and threat investigation endpoints.
"""
import asyncio
import csv
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.logger import get_logger
from src.common.utils import get_project_root, load_config, load_detection_rules
from src.database.mongodb import MongoDBManager
from src.hdfs.hdfs_manager import HDFSManager
from src.streaming.event_producer import StreamingEventProducer
from src.streaming.pipeline import StreamingPipeline
from src.data.schema import NetworkEvent

logger = get_logger("fastapi_server")

app = FastAPI(
    title="SENTINEL Cyber Threat Intelligence API",
    description="Real-Time SOC Backend powering Big Data Analytics and Stream Intelligence",
    version="2.0.0"
)

# Enable CORS for React Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Global Engine State Singletons
# ------------------------------------------------------------------------------
class SOCEngineState:
    def __init__(self):
        self.config = load_config()
        self.db = MongoDBManager(self.config)
        self.hdfs = HDFSManager(self.config)
        self.pipeline = StreamingPipeline(db_manager=self.db)
        self.producer = StreamingEventProducer(mode="NORMAL")
        self.is_streaming = False

        # Live telemetry buffers
        self.recent_raw_events: List[Dict[str, Any]] = []
        self.traffic_history: List[Dict[str, Any]] = []  # time-series rate samples
        self.demo_status: Dict[str, Any] = {
            "is_running": False,
            "current_phase": None,
            "progress_pct": 0,
            "message": "Ready"
        }
        self.lock = threading.Lock()

        # Connect event pipeline
        self._setup_event_dispatch()

    def _setup_event_dispatch(self):
        original_process = self.pipeline.process_event

        def hooked_process(event: NetworkEvent):
            with self.lock:
                self.recent_raw_events.append(event.to_dict())
                if len(self.recent_raw_events) > 60:
                    self.recent_raw_events.pop(0)
            return original_process(event)

        self._hooked_process = hooked_process

    def start_stream(self):
        if not self.is_streaming:
            self.producer.start_streaming(on_event_callback=self._hooked_process)
            self.is_streaming = True
            logger.info("Streaming producer started via API.")

    def stop_stream(self):
        if self.is_streaming:
            self.producer.stop_streaming()
            self.is_streaming = False
            logger.info("Streaming producer stopped via API.")

    def set_mode(self, mode: str):
        self.producer.set_mode(mode)
        if not self.is_streaming:
            self.start_stream()


soc_state = SOCEngineState()

# ------------------------------------------------------------------------------
# Background Telemetry Sampler
# ------------------------------------------------------------------------------
def traffic_sampler_worker():
    """Continuously samples throughput every second for live time-series charts."""
    while True:
        try:
            tel = soc_state.pipeline.get_pipeline_telemetry()
            now_iso = datetime.now(timezone.utc).strftime("%H:%M:%S")
            sample = {
                "timestamp": now_iso,
                "rate": tel["events_per_second"],
                "active_window": tel["active_window_events"],
                "threats": tel["threats_detected"],
                "mode": soc_state.producer.mode
            }
            with soc_state.lock:
                soc_state.traffic_history.append(sample)
                if len(soc_state.traffic_history) > 60:
                    soc_state.traffic_history.pop(0)
        except Exception as e:
            logger.debug(f"Telemetry sampler error: {e}")
        time.sleep(1.0)


sampler_thread = threading.Thread(target=traffic_sampler_worker, daemon=True)
sampler_thread.start()

# ------------------------------------------------------------------------------
# WebSocket Manager for Real-Time SOC Stream
# ------------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        encoded = jsonable_encoder(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_json(encoded)
            except Exception:
                self.disconnect(connection)


ws_manager = ConnectionManager()


@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Gather complete live snapshot
            tel = soc_state.pipeline.get_pipeline_telemetry()
            with soc_state.lock:
                recent_evs = list(soc_state.recent_raw_events[-15:])
                traffic_pts = list(soc_state.traffic_history[-30:])

            recent_alerts = soc_state.db.query_recent_alerts(limit=15)
            suspicious = soc_state.db.get_top_suspicious_ips(limit=10)
            threat_dist = soc_state.db.get_threat_distribution()

            payload = {
                "type": "TELEMETRY_UPDATE",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "engine": {
                    "is_streaming": soc_state.is_streaming,
                    "mode": soc_state.producer.mode,
                    "target_rate_eps": soc_state.producer.current_rate,
                    "uptime_seconds": tel["uptime_seconds"],
                    "events_processed": tel["events_processed"],
                    "events_per_second": tel["events_per_second"],
                    "threats_detected": tel["threats_detected"],
                    "critical_alerts": tel["critical_alerts"],
                },
                "sliding_window": {
                    "active_events": tel["active_window_events"],
                    "active_ips": tel["active_unique_ips"],
                    "window_duration_seconds": 300
                },
                "bloom_filter": tel["bloom_filter"],
                "traffic_history": traffic_pts,
                "recent_events": recent_evs,
                "recent_alerts": recent_alerts,
                "top_suspicious_ips": suspicious,
                "threat_distribution": threat_dist,
                "demo_status": soc_state.demo_status,
                "services": {
                    "mongodb": soc_state.db.is_connected(),
                    "hdfs_native": soc_state.hdfs.is_native_active
                }
            }

            await websocket.send_json(jsonable_encoder(payload))
            await asyncio.sleep(0.8)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket telemetry error: {e}", exc_info=True)
        ws_manager.disconnect(websocket)

# ------------------------------------------------------------------------------
# REST API Endpoints
# ------------------------------------------------------------------------------

@app.get("/api/health")
def get_system_health():
    """Return live system component health status."""
    return {
        "status": "OPERATIONAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "mongodb": {
                "status": "UP" if soc_state.db.is_connected() else "FALLBACK_MEMORY",
                "uri": soc_state.db.mongo_uri,
                "database": soc_state.db.db_name
            },
            "hdfs": {
                "status": "UP" if soc_state.hdfs.is_native_active else "EMULATED_LOCAL",
                "endpoint": soc_state.hdfs.webhdfs_url,
                "emulated_base": str(soc_state.hdfs.emulated_base)
            },
            "streaming_engine": {
                "status": "RUNNING" if soc_state.is_streaming else "STOPPED",
                "mode": soc_state.producer.mode
            }
        }
    }


@app.get("/api/telemetry")
def get_current_telemetry():
    """Return atomic telemetry snapshot."""
    tel = soc_state.pipeline.get_pipeline_telemetry()
    return {
        "telemetry": tel,
        "mode": soc_state.producer.mode,
        "is_streaming": soc_state.is_streaming,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/alerts")
def get_recent_alerts(limit: int = 50, min_severity: Optional[str] = None):
    """Retrieve recent threat alerts from MongoDB or memory buffer."""
    alerts = soc_state.db.query_recent_alerts(limit=limit, min_severity=min_severity)
    return {"count": len(alerts), "alerts": alerts}


@app.get("/api/suspicious-ips")
def get_suspicious_ips(limit: int = 15):
    """Retrieve ranked suspicious source IPs."""
    ips = soc_state.db.get_top_suspicious_ips(limit=limit)
    return {"count": len(ips), "items": ips}


@app.get("/api/threat-distribution")
def get_threat_distribution():
    """Retrieve category breakdown of detected threats."""
    dist = soc_state.db.get_threat_distribution()
    return {"distribution": dist}


@app.get("/api/traffic-history")
def get_traffic_history():
    """Retrieve historical event rate time-series points."""
    with soc_state.lock:
        history = list(soc_state.traffic_history)
    return {"history": history}


@app.get("/api/events")
def get_recent_events(limit: int = 30):
    """Retrieve latest raw network flow events."""
    with soc_state.lock:
        events = list(soc_state.recent_raw_events[-limit:])
    return {"count": len(events), "events": events}


@app.get("/api/investigation/{ip}")
def investigate_host(ip: str):
    """Detailed host threat investigation profile."""
    # Check sliding window metrics
    win_metrics = soc_state.pipeline.sliding_window.get_host_metrics(ip)

    # Check alert history for this IP
    all_alerts = soc_state.db.query_recent_alerts(limit=100)
    host_alerts = [a for a in all_alerts if a.get("source_ip") == ip]

    # Check Bloom filter membership
    in_bloom = soc_state.pipeline.bloom_filter.contains(ip)

    # Estimate protocol & port behavior
    port_counts = {}
    total_events = 0
    threat_score = 0.0
    severity = "LOW"
    detection_reason = "Normal telemetry profile"

    if win_metrics:
        total_events = win_metrics["event_count"]
    if host_alerts:
        threat_score = max(a.get("threat_score", 0.0) for a in host_alerts)
        severity = host_alerts[0].get("severity", "MEDIUM")
        detection_reason = host_alerts[0].get("detection_reason", "")
        # Aggregate unique ports from alerts
        for a in host_alerts:
            total_events = max(total_events, a.get("event_count", 0))

    return {
        "source_ip": ip,
        "is_known_in_bloom_filter": in_bloom,
        "threat_score": threat_score,
        "severity": severity,
        "total_observed_events": total_events,
        "detection_reason": detection_reason,
        "active_window_metrics": win_metrics,
        "related_alerts": host_alerts,
        "investigation_timestamp": datetime.now(timezone.utc).isoformat()
    }


class ModeRequest(BaseModel):
    mode: str


@app.post("/api/simulation/start")
def start_simulation():
    soc_state.start_stream()
    return {"status": "SUCCESS", "is_streaming": True, "mode": soc_state.producer.mode}


@app.post("/api/simulation/stop")
def stop_simulation():
    soc_state.stop_stream()
    return {"status": "SUCCESS", "is_streaming": False}


@app.post("/api/simulation/mode")
def set_simulation_mode(req: ModeRequest):
    valid_modes = {"NORMAL", "DDOS", "PORT_SCAN", "ANOMALY"}
    norm = req.mode.upper()
    if norm not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid simulation mode: {req.mode}")
    soc_state.set_mode(norm)
    return {"status": "SUCCESS", "mode": soc_state.producer.mode, "is_streaming": soc_state.is_streaming}


@app.post("/api/alerts/clear")
def clear_alerts():
    soc_state.db.clear_database()
    soc_state.pipeline.recent_alerts.clear()
    with soc_state.lock:
        soc_state.recent_raw_events.clear()
        soc_state.traffic_history.clear()
    return {"status": "SUCCESS", "message": "Alerts and telemetry history cleared."}


# ------------------------------------------------------------------------------
# Academic Demo Scenario Runner
# ------------------------------------------------------------------------------
def demo_orchestrator_thread(step_duration: int = 4):
    soc_state.demo_status["is_running"] = True
    soc_state.start_stream()

    phases = [
        ("PHASE 1: Baseline Normal Workload", "NORMAL", "Establishing baseline telemetry. Expecting stable flow.", 15),
        ("PHASE 2: Volumetric DDoS Simulation", "DDOS", "Simulating massive burst. Expecting CRITICAL DDoS alert.", 35),
        ("PHASE 3: Normal Traffic Recovery", "NORMAL", "Traffic returning to safe parameters.", 50),
        ("PHASE 4: Port Scan Reconnaissance", "PORT_SCAN", "Rapid port sweeps with failures. Expecting HIGH Port-Scan alert.", 70),
        ("PHASE 5: Covert Channel / Anomaly", "ANOMALY", "Simulating asymmetric data exfiltration on non-standard ports.", 85),
        ("PHASE 6: Return to Baseline", "NORMAL", "Stabilization and reporting complete.", 100)
    ]

    try:
        for phase_name, mode, desc, pct in phases:
            soc_state.demo_status["current_phase"] = phase_name
            soc_state.demo_status["message"] = desc
            soc_state.demo_status["progress_pct"] = pct
            soc_state.set_mode(mode)
            time.sleep(step_duration)

        soc_state.demo_status["message"] = "Demonstration sequence successfully completed."
    except Exception as e:
        soc_state.demo_status["message"] = f"Error in demo sequence: {e}"
    finally:
        soc_state.demo_status["is_running"] = False


@app.post("/api/simulation/demo")
def trigger_demo_scenario(background_tasks: BackgroundTasks, step_duration: int = 4):
    if soc_state.demo_status["is_running"]:
        return {"status": "ALREADY_RUNNING", "demo_status": soc_state.demo_status}

    background_tasks.add_task(demo_orchestrator_thread, step_duration)
    return {"status": "STARTED", "message": "Academic demo scenario initiated."}


# ------------------------------------------------------------------------------
# Big Data Pipeline & Analytics REST Endpoints
# ------------------------------------------------------------------------------

@app.get("/api/bigdata/status")
def get_bigdata_status():
    root = get_project_root()
    mr_dir = root / "results" / "mapreduce"
    spark_dir = root / "results" / "spark"
    data_dir = root / "data" / "generated"

    datasets = list(data_dir.glob("*.csv")) if data_dir.exists() else []
    has_mr = (mr_dir / "mapreduce_top_ips.csv").exists()
    has_spark = (spark_dir / "cluster_summary.csv").exists()

    return {
        "datasets_generated": [f.name for f in datasets],
        "hdfs": {
            "mode": "NATIVE" if soc_state.hdfs.is_native_active else "EMULATED_LOCAL",
            "directories": soc_state.hdfs.config.get("hdfs", {}).get("directories", {})
        },
        "mapreduce": {
            "executed": has_mr,
            "last_modified": datetime.fromtimestamp((mr_dir / "mapreduce_top_ips.csv").stat().st_mtime).isoformat() if has_mr else None
        },
        "spark": {
            "executed": has_spark,
            "last_modified": datetime.fromtimestamp((spark_dir / "cluster_summary.csv").stat().st_mtime).isoformat() if has_spark else None
        }
    }


@app.get("/api/bigdata/mapreduce")
def get_mapreduce_analytics():
    root = get_project_root()
    mr_dir = root / "results" / "mapreduce"

    top_ips_file = mr_dir / "mapreduce_top_ips.csv"
    attack_counts_file = mr_dir / "mapreduce_attack_counts.csv"

    top_ips = []
    if top_ips_file.exists():
        with open(top_ips_file, "r", encoding="utf-8") as f:
            top_ips = list(csv.DictReader(f))[:20]

    attack_counts = []
    if attack_counts_file.exists():
        with open(attack_counts_file, "r", encoding="utf-8") as f:
            attack_counts = list(csv.DictReader(f))

    return {
        "executed": bool(top_ips or attack_counts),
        "top_ips": top_ips,
        "attack_counts": attack_counts
    }


@app.get("/api/bigdata/spark")
def get_spark_analytics():
    root = get_project_root()
    spark_dir = root / "results" / "spark"

    summary_file = spark_dir / "cluster_summary.csv"
    clusters_file = spark_dir / "spark_clusters.csv"

    summary = []
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = list(csv.DictReader(f))

    clusters_sample = []
    if clusters_file.exists():
        with open(clusters_file, "r", encoding="utf-8") as f:
            clusters_sample = list(csv.DictReader(f))[:30]

    return {
        "executed": bool(summary),
        "cluster_summary": summary,
        "clusters_sample": clusters_sample
    }


@app.get("/api/bigdata/reports")
def get_performance_reports():
    root = get_project_root()
    report_csv = root / "results" / "reports" / "scalability_experiment.csv"
    report_md = root / "results" / "reports" / "scalability_experiment.md"

    csv_data = []
    if report_csv.exists():
        with open(report_csv, "r", encoding="utf-8") as f:
            csv_data = list(csv.DictReader(f))

    md_text = ""
    if report_md.exists():
        with open(report_md, "r", encoding="utf-8") as f:
            md_text = f.read()

    return {
        "available": bool(csv_data),
        "benchmark_rows": csv_data,
        "markdown_report": md_text
    }


# ------------------------------------------------------------------------------
# Network Topology Visualizer Endpoint
# ------------------------------------------------------------------------------
@app.get("/api/network/topology")
def get_network_topology():
    """Generates real network graph nodes and active communication paths."""
    target_servers = [
        {"id": "srv-1", "label": "10.0.0.5 (Primary Web/App)", "type": "server", "status": "targeted", "x": 550, "y": 140},
        {"id": "srv-2", "label": "10.0.0.10 (API Gateway)", "type": "server", "status": "normal", "x": 550, "y": 240},
        {"id": "srv-3", "label": "10.0.0.15 (Core Database)", "type": "server", "status": "normal", "x": 550, "y": 340},
    ]

    gateways = [
        {"id": "gw-fw", "label": "Edge Firewall / IPS", "type": "gateway", "status": "filtering", "x": 350, "y": 240}
    ]

    # Extract active source IPs from sliding window or recent alerts
    alerts = soc_state.db.query_recent_alerts(limit=10)
    alert_ips = {a["source_ip"]: a for a in alerts}

    active_hosts = soc_state.pipeline.sliding_window.get_all_active_hosts()[:6]
    if not active_hosts:
        active_hosts = ["192.168.1.45", "192.168.1.12", "185.220.101.5", "198.18.0.42"]

    client_nodes = []
    y_step = 60
    for idx, host in enumerate(active_hosts):
        severity = alert_ips[host]["severity"] if host in alert_ips else "LOW"
        node_status = "critical" if severity == "CRITICAL" else ("high" if severity == "HIGH" else "normal")
        client_nodes.append({
            "id": f"src-{idx}",
            "ip": host,
            "label": host,
            "type": "client",
            "status": node_status,
            "severity": severity,
            "x": 120,
            "y": 100 + idx * y_step
        })

    edges = []
    for c in client_nodes:
        edges.append({
            "from": c["id"],
            "to": "gw-fw",
            "status": c["status"]
        })

    edges.append({"from": "gw-fw", "to": "srv-1", "status": "critical" if any(c["status"] == "critical" for c in client_nodes) else "normal"})
    edges.append({"from": "gw-fw", "to": "srv-2", "status": "normal"})
    edges.append({"from": "gw-fw", "to": "srv-3", "status": "normal"})

    return {
        "nodes": client_nodes + gateways + target_servers,
        "edges": edges,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ------------------------------------------------------------------------------
# Pipeline Job Trigger Execution Endpoints
# ------------------------------------------------------------------------------
class JobTriggerRequest(BaseModel):
    events: Optional[int] = 50000


@app.post("/api/bigdata/run/generate")
def trigger_data_generation(req: JobTriggerRequest):
    root = get_project_root()
    cmd = [sys.executable, str(root / "scripts" / "generate_data.py"), "--events", str(req.events)]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=res.stderr)
    return {"status": "SUCCESS", "output": res.stdout}


@app.post("/api/bigdata/run/hdfs")
def trigger_hdfs_upload():
    root = get_project_root()
    cmd = [sys.executable, str(root / "scripts" / "upload_to_hdfs.py"), "--dest", "/cyber-threat/raw/", "--list"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=res.stderr)
    return {"status": "SUCCESS", "output": res.stdout}


@app.post("/api/bigdata/run/mapreduce")
def trigger_mapreduce():
    root = get_project_root()
    cmd = [sys.executable, str(root / "scripts" / "run_mapreduce.py")]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=res.stderr)
    return {"status": "SUCCESS", "output": res.stdout}


@app.post("/api/bigdata/run/spark")
def trigger_spark():
    root = get_project_root()
    cmd = [sys.executable, str(root / "scripts" / "run_spark.py")]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=res.stderr)
    return {"status": "SUCCESS", "output": res.stdout}


@app.post("/api/bigdata/run/seed")
def trigger_seed_mongodb():
    root = get_project_root()
    cmd = [sys.executable, str(root / "scripts" / "seed_mongodb.py")]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=res.stderr)
    return {"status": "SUCCESS", "output": res.stdout}


@app.get("/api/config")
def get_system_config():
    return {
        "config": load_config(),
        "detection_rules": load_detection_rules()
    }


# Mount built React frontend static assets if available
dist_dir = PROJECT_ROOT / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static_frontend")


# Standalone runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, reload=False)
