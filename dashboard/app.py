"""Streamlit Real-Time Cyber Threat Detection & Network Intelligence Dashboard."""
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import streamlit as st

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dashboard.components import render_bloom_filter_card, render_kpi_cards, render_severity_badge
from dashboard.queries import (
    fetch_recent_alerts,
    fetch_top_suspicious_ips,
    fetch_threat_distribution,
    get_db_instance,
    load_mapreduce_results,
    load_spark_results
)
from src.database.mongodb import MongoDBManager
from src.streaming.event_producer import StreamingEventProducer
from src.streaming.pipeline import StreamingPipeline

# ------------------------------------------------------------------------------
# Page Setup
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Cyber Threat Intelligence | Big Data Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# Persistent Session State Initialization
# ------------------------------------------------------------------------------
if "db" not in st.session_state:
    st.session_state.db = MongoDBManager()

if "pipeline" not in st.session_state:
    st.session_state.pipeline = StreamingPipeline(db_manager=st.session_state.db)

if "producer" not in st.session_state:
    st.session_state.producer = StreamingEventProducer(mode="NORMAL")

if "traffic_history" not in st.session_state:
    st.session_state.traffic_history = []  # list of {"time": str, "rate": float, "mode": str}

if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

# ------------------------------------------------------------------------------
# Background Stream Handling
# ------------------------------------------------------------------------------
def start_stream():
    if not st.session_state.is_streaming:
        st.session_state.producer.start_streaming(on_event_callback=st.session_state.pipeline.process_event)
        st.session_state.is_streaming = True

def stop_stream():
    if st.session_state.is_streaming:
        st.session_state.producer.stop_streaming()
        st.session_state.is_streaming = False

def switch_attack_mode(mode: str):
    st.session_state.producer.set_mode(mode)
    if not st.session_state.is_streaming:
        start_stream()

# ------------------------------------------------------------------------------
# Sidebar: Attack Simulation Controls & Telemetry
# ------------------------------------------------------------------------------
with st.sidebar:
    st.title("🛡️ Threat Simulation")
    st.markdown("Control network telemetry generators to evaluate real-time detector response.")

    # Streaming Engine Toggle
    stream_col1, stream_col2 = st.columns(2)
    with stream_col1:
        if st.button("▶️ Start Stream", use_container_width=True, type="primary"):
            start_stream()
            st.rerun()
    with stream_col2:
        if st.button("⏹️ Stop Stream", use_container_width=True):
            stop_stream()
            st.rerun()

    current_status = "🟢 RUNNING" if st.session_state.is_streaming else "🔴 STOPPED"
    active_mode = st.session_state.producer.mode
    st.markdown(f"**Engine Status:** `{current_status}` | **Mode:** `{active_mode}`")

    st.markdown("---")
    st.subheader("Simulate Attack Profiles")

    if st.button("🟢 Normal Traffic", use_container_width=True):
        switch_attack_mode("NORMAL")
        st.rerun()

    if st.button("🚨 Simulate DDoS Flood", use_container_width=True):
        switch_attack_mode("DDOS")
        st.rerun()

    if st.button("🔍 Simulate Port Scan", use_container_width=True):
        switch_attack_mode("PORT_SCAN")
        st.rerun()

    if st.button("⚠️ Simulate Anomaly / Exfiltration", use_container_width=True):
        switch_attack_mode("ANOMALY")
        st.rerun()

    st.markdown("---")
    st.subheader("Database Operations")
    if st.button("🧹 Clear Alerts History", use_container_width=True):
        st.session_state.db.clear_database()
        st.session_state.pipeline.recent_alerts.clear()
        st.session_state.traffic_history.clear()
        st.success("Alerts history cleared.")
        st.rerun()

    # Auto refresh checkbox
    auto_refresh = st.checkbox("Auto-refresh (every 2s)", value=st.session_state.is_streaming)
    if auto_refresh:
        time.sleep(2.0)
        st.rerun()

# ------------------------------------------------------------------------------
# Dashboard Header
# ------------------------------------------------------------------------------
st.title("Real-Time Cyber Threat Detection & Network Intelligence")
st.caption("Big Data Analytics System: HDFS · Hadoop MapReduce · Apache Spark MLlib · Real-Time Sliding Window · Bloom Filter · MongoDB")

# Record traffic history for charts
tel = st.session_state.pipeline.get_pipeline_telemetry()
now_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
st.session_state.traffic_history.append({
    "time": now_str,
    "rate": tel["events_per_second"],
    "mode": st.session_state.producer.mode
})
# Keep last 40 data points
if len(st.session_state.traffic_history) > 40:
    st.session_state.traffic_history.pop(0)

# ------------------------------------------------------------------------------
# Top KPI Cards
# ------------------------------------------------------------------------------
db = st.session_state.db
suspicious_df = fetch_top_suspicious_ips(db, limit=50)
num_suspicious = len(suspicious_df)

render_kpi_cards(
    total_events=tel["events_processed"],
    eps=tel["events_per_second"],
    threats_detected=tel["threats_detected"],
    critical_alerts=tel["critical_alerts"],
    suspicious_ips=num_suspicious
)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Main Dashboard Tabs
# ------------------------------------------------------------------------------
tab_stream, tab_historical, tab_architecture = st.tabs([
    "⚡ Real-Time Streaming & Live Defense",
    "📊 Historical Big Data Analytics (Spark & MapReduce)",
    "🏗️ Distributed Architecture & Big Data Principles"
])

# ==============================================================================
# TAB 1: Real-Time Streaming & Threat Detection
# ==============================================================================
with tab_stream:
    col_chart, col_dist = st.columns([2, 1])

    with col_chart:
        st.subheader("📈 Live Network Traffic Rate (Events / Sec)")
        if st.session_state.traffic_history:
            chart_df = pd.DataFrame(st.session_state.traffic_history)
            st.line_chart(chart_df.set_index("time")["rate"])
            st.caption("Visibly monitors volumetric surge. High spikes indicate DDoS attack bursts.")
        else:
            st.info("Start the stream to view live traffic rates.")

    with col_dist:
        st.subheader("🎯 Threat Distribution")
        dist_df = fetch_threat_distribution(db)
        if not dist_df.empty and dist_df["count"].sum() > 0:
            st.bar_chart(dist_df.set_index("threat_type")["count"])
        else:
            st.info("No active threats recorded yet.")

    st.markdown("---")

    # Top Suspicious IPs and Detection State
    col_ips, col_state = st.columns([3, 2])

    with col_ips:
        st.subheader("🚨 Top Suspicious Source IPs")
        if not suspicious_df.empty:
            display_ips = suspicious_df.copy()
            # Format display columns
            display_ips["threat_score"] = display_ips["threat_score"].apply(lambda s: f"{s:.2f}")
            st.dataframe(
                display_ips[["source_ip", "threat_score", "severity", "threat_types", "event_count", "last_seen"]],
                use_container_width=True,
                height=220
            )
        else:
            st.info("No suspicious IP anomalies logged.")

    with col_state:
        st.subheader("⚙️ Detection Engine & Sliding Window Status")
        win_evs = tel["active_window_events"]
        win_ips = tel["active_unique_ips"]

        st.markdown(f"- **Streaming Engine:** `{current_status}`")
        st.markdown(f"- **Current Attack Mode:** `{active_mode}`")
        st.markdown(f"- **Active 5-Min Window Events:** `{win_evs:,}`")
        st.markdown(f"- **Active Hosts in Window:** `{win_ips:,}`")
        st.markdown(f"- **MongoDB Connection:** `{'CONNECTED (localhost:27017)' if tel['mongodb_connected'] else 'OFFLINE'}`")

    st.markdown("---")

    # Bloom Filter Telemetry
    render_bloom_filter_card(tel["bloom_filter"])

    st.markdown("---")

    # Live Alerts Feed
    st.subheader("🔔 Live Threat Alerts Feed (Recent 50)")
    alerts_df = fetch_recent_alerts(db, limit=50)

    if not alerts_df.empty:
        # Render formatted table with colored severity badges
        for idx, row in alerts_df.head(15).iterrows():
            badge = render_severity_badge(row['severity'])
            st.markdown(
                f"<div style='border-left: 4px solid #0d6efd; padding: 6px 12px; margin-bottom: 8px; background-color: rgba(255,255,255,0.03); border-radius: 4px;'>"
                f"<b>{row['timestamp']}</b> &nbsp;|&nbsp; {badge} &nbsp;|&nbsp; <b>{row['threat_type']}</b> &nbsp;|&nbsp; "
                f"Source: <code>{row['source_ip']}</code> &nbsp;|&nbsp; Score: <b>{row['threat_score']}</b><br>"
                f"<span style='color: #adb5bd; font-size: 13px;'>{row['detection_reason']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No alerts generated yet. Trigger an attack simulation from the sidebar.")

# ==============================================================================
# TAB 2: Historical Big Data Analytics (Spark & MapReduce)
# ==============================================================================
with tab_historical:
    st.header("Historical Big Data Processing Pipeline")
    st.markdown("Demonstrating offline distributed batch processing using Hadoop MapReduce and Apache Spark MLlib.")

    mr_results = load_mapreduce_results()
    spark_results = load_spark_results()

    st.subheader("1. Hadoop MapReduce Batch Aggregations")
    col_mr1, col_mr2 = st.columns(2)

    with col_mr1:
        st.markdown("#### Job 1: High-Volume Source IPs (MapReduce)")
        if "top_ips" in mr_results:
            st.dataframe(mr_results["top_ips"].head(10), use_container_width=True)
        else:
            st.warning("MapReduce outputs not found. Run: `python scripts/run_mapreduce.py`")

    with col_mr2:
        st.markdown("#### Job 2: Attack Classification Frequency (MapReduce)")
        if "attack_counts" in mr_results:
            st.dataframe(mr_results["attack_counts"], use_container_width=True)
            st.bar_chart(mr_results["attack_counts"].set_index("attack_type")["event_count"])
        else:
            st.warning("Run `python scripts/run_mapreduce.py` to generate attack frequency counts.")

    st.markdown("---")

    st.subheader("2. Apache Spark MLlib K-Means Host Behavioral Clustering")
    st.markdown(
        "PySpark computed 8 numerical behavioral features for all hosts, standardized them using `StandardScaler`, "
        "and trained an MLlib K-Means model to discover distinct behavioral archetypes."
    )

    if "cluster_summary" in spark_results:
        c_summary = spark_results["cluster_summary"]
        st.dataframe(c_summary, use_container_width=True)

        st.markdown("#### Cluster Centroid Behavioral Profiles:")
        for _, row in c_summary.iterrows():
            cid = int(row['cluster'])
            st.markdown(
                f"- **Cluster {cid} [{row['threat_severity']}]:** `{row['assigned_profile']}` "
                f"({int(row['host_count'])} hosts) &mdash; {row['detection_rationale']}"
            )
    else:
        st.warning("Spark cluster results not found. Run: `python scripts/run_spark.py`")

    if "ip_clusters" in spark_results:
        st.markdown("#### Host-Level Cluster Assignments (Sample)")
        st.dataframe(spark_results["ip_clusters"].head(15), use_container_width=True)

# ==============================================================================
# TAB 3: Architecture & Big Data Concepts
# ==============================================================================
with tab_architecture:
    st.header("Cyber Threat Intelligence Architecture")

    st.markdown("""
    ```
                             ┌──────────────────────┐
                             │ Network Event Source │
                             │ Dataset + Generator  │
                             └──────────┬───────────┘
                                        │
                       ┌────────────────┴────────────────┐
                       │                                 │
                       ▼                                 ▼
              HISTORICAL BATCH PATH              REAL-TIME PATH
                       │                                 │
                       ▼                                 ▼
                      HDFS                     Traffic/Event Producer
                       │                                 │
                       ▼                                 ▼
                  MapReduce                    Streaming Detector
                       │                                 │
                       ▼                          ┌──────┴──────┐
                Aggregated Data                  │             │
                       │                    Sliding Window  Bloom Filter
                       ▼                          │             │
                     Spark                       └──────┬──────┘
                       │                                 │
              ┌────────┴─────────┐                       ▼
              │                  │                 Threat Scoring
              ▼                  ▼                       │
     Feature Engineering    K-Means                      │
              │              Clustering                  │
              └────────┬─────────┘                       │
                       │                                 │
                       └────────────┬────────────────────┘
                                    ▼
                                 MongoDB
                                    │
                                    ▼
                             Streamlit Dashboard
    ```
    """)

    st.markdown("### The 5 V's of Big Data in this Project:")
    v1, v2 = st.columns(2)
    with v1:
        st.markdown("""
        - **Volume:** Scalable synthesis and ingestion of millions of atomic network events.
        - **Velocity:** Sub-millisecond sliding window evaluation and real-time streaming detection.
        - **Variety:** Diverse telemetry comprising TCP, UDP, ICMP, port distributions, duration, and status flags.
        """)
    with v2:
        st.markdown("""
        - **Veracity:** Probabilistic validation (Bloom Filter) and multi-factor heuristic threat scoring.
        - **Value:** Actionable cybersecurity intelligence identifying active DDoS floods, port scans, and data exfiltration.
        """)
