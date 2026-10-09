"""Streamlit UI Component renderers for Cyber Threat Intelligence."""
import streamlit as st
import pandas as pd
from typing import Any, Dict


def render_kpi_cards(
    total_events: int,
    eps: float,
    threats_detected: int,
    critical_alerts: int,
    suspicious_ips: int
) -> None:
    """Render the 5 headline KPI metric cards."""
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric(label="Total Events", value=f"{total_events:,}")
    with c2:
        st.metric(label="Events / Sec", value=f"{eps:.1f}")
    with c3:
        st.metric(label="Threats Detected", value=f"{threats_detected:,}")
    with c4:
        st.metric(label="Critical Alerts", value=f"{critical_alerts:,}", delta=None if critical_alerts == 0 else f"+{critical_alerts}")
    with c5:
        st.metric(label="Suspicious IPs", value=f"{suspicious_ips:,}")


def render_severity_badge(severity: str) -> str:
    """Format severity level with high-contrast colored HTML pill."""
    colors = {
        "CRITICAL": "#dc3545",
        "HIGH": "#fd7e14",
        "MEDIUM": "#ffc107",
        "LOW": "#28a745"
    }
    bg = colors.get(str(severity).upper(), "#6c757d")
    text_color = "#ffffff" if severity != "MEDIUM" else "#000000"
    return f"<span style='background-color:{bg}; color:{text_color}; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:12px;'>{severity}</span>"


def render_bloom_filter_card(bf_stats: Dict[str, Any]) -> None:
    """Render Bloom Filter operational statistics."""
    st.markdown("### 🔍 Bloom Filter State (Probabilistic Membership)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Elements Ingested", f"{bf_stats.get('elements_added', 0):,}")
    with col2:
        st.metric("Memory Allocated", f"{bf_stats.get('memory_usage_kb', 0):.1f} KB")
    with col3:
        st.metric("Hash Functions (k)", f"{bf_stats.get('num_hash_functions', 0)}")
    with col4:
        fpp = bf_stats.get('current_fpp', 0.0)
        st.metric("Estimated FPP", f"{fpp:.6f}")

    fill_pct = bf_stats.get('fill_ratio', 0.0) * 100
    st.progress(min(fill_pct / 100.0, 1.0), text=f"Bit Array Density: {fill_pct:.2f}% set")
