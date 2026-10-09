# System Architecture & Technical Design

## 1. High-Level Architecture Overview

The system implements a unified **Lambda-Style Big Data Architecture** for cyber threat intelligence, supporting both **Historical Distributed Batch Analytics** and **Real-Time Low-Latency Streaming Threat Detection**.

```
                         ┌────────────────────────────────────────┐
                         │       Network Event Telemetry          │
                         │   Synthetic Flow Generator (10M scale) │
                         └──────────────────┬─────────────────────┘
                                            │
                   ┌────────────────────────┴────────────────────────┐
                   │                                                 │
                   ▼                                                 ▼
        [ HISTORICAL BATCH PATH ]                          [ REAL-TIME STREAMING PATH ]
                   │                                                 │
                   ▼                                                 ▼
        HDFS Distributed Storage                           Event Producer (Dynamic Mode)
       (/cyber-threat/raw, etc.)                           (Normal, DDoS, PortScan, Anomaly)
                   │                                                 │
                   ▼                                                 ▼
        Hadoop MapReduce Engine                            Streaming Detection Engine
     - Job 1: Host Event Volumes                                     │
     - Job 2: Attack Classification                         ┌────────┴────────┐
     - Job 3: Port Activity Analysis                        ▼                 ▼
                   │                                 Sliding Window     Bloom Filter
                   ▼                                (5-min Rolling)   (Set Membership)
        Aggregated Flow Features                            │                 │
                   │                                        └────────┬────────┘
                   ▼                                                 │
        Apache Spark 4.2.0 Engine                                    ▼
       - Feature Engineering (Scaling)                         Multi-Detector
       - MLlib K-Means Clustering                              (DDoS, Port Scan,
       - Behavioral Heuristic Profiler                          Covert Anomaly)
                   │                                                 │
                   │                                                 ▼
                   │                                         Threat Scoring
                   │                                      [0.0 - 1.0 Normalized]
                   │                                                 │
                   └────────────────────────┬────────────────────────┘
                                            ▼
                                  MongoDB NoSQL Storage
                             (Collections: alerts, aggregates)
                                            │
                                            ▼
                               Streamlit Interactive Dashboard
```

---

## 2. Component Design & Interconnection

### 2.1 Network Telemetry Source
- Produces atomic network telemetry adhering to a strict 12-field schema.
- Configurable generator outputs normal enterprise baselines alongside distinct attack patterns:
  - **DDoS Floods:** Extreme packet and byte burst rates, concentrated port targeting.
  - **Port Scans:** Horizontal sweeps across destination ports with high connection rejection rates.
  - **Anomalous Exfiltration:** High byte ratio asymmetry and covert non-standard ports.

### 2.2 Historical Batch Path
1. **HDFS Storage Layer (`src/hdfs/hdfs_manager.py`):**
   - Manages logical directories: `/cyber-threat/raw`, `/cyber-threat/processed`, `/cyber-threat/features`, `/cyber-threat/results`.
   - Connects via WebHDFS protocol to native clusters with structured local emulated fallback.
2. **Hadoop MapReduce Engine (`src/mapreduce/`):**
   - Standard Map-Sort-Reduce streaming jobs processing millions of events.
   - Computes heavy-volume host frequencies, attack category distributions, and port activity profiles.
3. **Apache Spark MLlib (`src/spark/`):**
   - Ingests distributed event logs into typed DataFrames.
   - Computes 8 numerical behavioral features per host (`event_count`, `total_bytes_sent`, `total_bytes_received`, `avg_packet_count`, `unique_dest_ports`, `failed_conn_count`, `avg_duration_ms`, `protocol_diversity`).
   - Standardizes features via `StandardScaler`.
   - Trains unsupervised K-Means clustering to discover latent host behaviors and assigns interpretable cybersecurity profiles.

### 2.3 Real-Time Streaming Path
1. **Streaming Event Producer (`src/streaming/event_producer.py`):**
   - Emits events continuously with runtime mode transitions.
2. **Bloom Filter (`src/streaming/bloom_filter.py`):**
   - Space-efficient probabilistic filter with double hashing verifying IP membership in sub-microsecond time.
3. **Sliding Window Tracker (`src/streaming/sliding_window.py`):**
   - 5-minute rolling window with deterministic time-based eviction.
   - Computes live flow rates (events/s, packets/s, bytes/s) and connection drop ratios.
4. **Multi-Detector Suite (`src/streaming/detectors.py`):**
   - Evaluates active window metrics against rules configured in `config/detection_rules.yaml`.
5. **Threat Scoring Engine (`src/streaming/threat_scorer.py`):**
   - Synthesizes multi-vector metrics into a unified normalized score [0.0 - 1.0] and maps to severity bands (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### 2.4 Storage & Visualization Layer
- **MongoDB NoSQL Database:** Stores time-indexed alerts and batch aggregates with compound indexes for low-latency queries.
- **Streamlit Real-Time Dashboard:** Interactive GUI featuring live KPI cards, traffic spike line charts, Bloom filter monitoring, top suspicious IP rankings, alert feeds, and historical analytics.
