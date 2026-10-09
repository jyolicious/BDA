# Real-Time Cyber Threat Detection & Network Intelligence Using Big Data Analytics

An end-to-end, technically credible Big Data Analytics system that integrates **distributed batch processing (HDFS, Hadoop MapReduce, Apache Spark MLlib)** with **low-latency real-time stream analytics (Sliding Windows, Bloom Filters, Space-Saving Heavy Hitters, Multi-Factor Threat Scoring)** and persistent NoSQL storage (**MongoDB**) visualized via an interactive **Streamlit Dashboard**.

---

## 1. Project Overview

Modern enterprise networks generate millions of flow events every second. Traditional relational database management systems and static intrusion detection systems fail to cope with the sheer volume, velocity, and variety of this network telemetry. 

This project demonstrates a production-grade, reproducible academic Big Data solution that bridges the gap between:
1. **Historical Deep Batch Analytics:** Offline distributed storage (HDFS), distributed MapReduce aggregations, and Apache Spark MLlib unsupervised clustering to extract host behavioral baselines.
2. **Real-Time Streaming Cyber Intelligence:** Millisecond-level stream processing utilizing a 5-minute sliding window, probabilistic Bloom Filter membership testing, bounded-memory heavy-hitter tracking, and explainable threat scoring.

---

## 2. Problem Statement

Cyber adversaries continuously employ distributed denial of service (DDoS) floods, automated port reconnaissance sweeps, and covert data exfiltration channels to breach infrastructure. Detecting these threats requires:
- Handling massive telemetry streams without memory exhaustion.
- Identifying volumetric spikes and rapid port traversal within active sliding windows.
- Distinguishing between routine server traffic and malicious attacks using verifiable data structures.
- Providing real-time situational awareness to Security Operations Center (SOC) analysts.

---

## 3. Project Objectives

- **High-Volume Telemetry Synthesis:** Generate reproducible network flow events conforming to a strict 12-attribute canonical schema across Normal, DDoS, Port-Scan, and Anomalous profiles.
- **Distributed Storage & Batch Analytics:** Ingest datasets into HDFS, execute multi-job Hadoop MapReduce streaming pipelines, and perform PySpark host feature engineering.
- **Unsupervised Machine Learning:** Train Spark MLlib K-Means models to segment hosts into interpretable behavioral profiles without requiring pre-labeled training data.
- **Sub-Millisecond Stream Detection:** Implement a 5-minute rolling sliding window, optimal Bloom Filter, and Space-Saving heavy-hitters tracker.
- **Explainable Threat Scoring:** Calculate composite threat scores $[0.0 - 1.0]$ with discrete severity banding (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Real-Time SOC Dashboard:** Deliver a live Streamlit GUI with interactive attack simulation controls, KPI telemetry, and threat charts.

---

## 4. Target Architecture

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

## 5. Technology Stack

- **Distributed Batch Analytics:** Apache Spark 4.2.0 (PySpark MLlib), Hadoop MapReduce (Streaming API)
- **Distributed Storage:** HDFS (WebHDFS client with structured local emulated fallback)
- **NoSQL Database:** MongoDB Server 8.0 / PyMongo (with compound indexing)
- **Stream Processing:** Python 3.13, Rolling Sliding Window Deque, Kirsch-Mitzenmacher Double-Hashing Bloom Filter, Space-Saving Heavy Hitters
- **User Interface:** Streamlit 1.65.0, Altair, Matplotlib
- **Testing & Verification:** PyTest 9.1

---

## 6. Directory Structure

```text
BDA/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── config/
│   ├── config.yaml                     # Cluster, database, and pipeline settings
│   └── detection_rules.yaml            # Thresholds and threat scoring weights
│
├── data/
│   ├── raw/
│   ├── generated/                      # Generated synthetic datasets
│   ├── processed/
│   ├── samples/                        # Sample event previews
│   └── hdfs_emulated/                  # Structured local HDFS filesystem mirror
│
├── src/
│   ├── data/
│   │   ├── schema.py                   # Canonical 12-field NetworkEvent schema
│   │   ├── generator.py                # Synthetic telemetry flow generator
│   │   └── dataset_loader.py           # CSV/DataFrame persistence and loaders
│   ├── hdfs/
│   │   └── hdfs_manager.py             # WebHDFS client and fallback manager
│   ├── mapreduce/
│   │   ├── mapper.py                   # Hadoop streaming mapper
│   │   ├── reducer.py                  # Hadoop streaming reducer
│   │   └── run_mapreduce.py            # Map-Sort-Reduce orchestrator
│   ├── spark/
│   │   ├── spark_session.py            # PySpark session configuration
│   │   ├── preprocessing.py            # Ingestion and schema casting
│   │   ├── aggregation.py              # Distributed source-IP aggregations
│   │   ├── feature_engineering.py      # VectorAssembler & StandardScaler
│   │   └── clustering.py               # MLlib KMeans & heuristic profiles
│   ├── streaming/
│   │   ├── event_producer.py           # Dynamic streaming generator
│   │   ├── sliding_window.py           # 5-minute rolling window tracker
│   │   ├── bloom_filter.py             # Probabilistic bit array filter
│   │   ├── frequent_items.py           # Space-Saving heavy-hitters tracker
│   │   ├── detectors.py                # DDoS, Port-Scan, and Anomaly engines
│   │   ├── threat_scorer.py            # Composite threat scoring formulation
│   │   └── pipeline.py                 # Integrated real-time pipeline engine
│   ├── database/
│   │   └── mongodb.py                  # MongoDB indexing, storage, and queries
│   └── common/
│       ├── logger.py                   # Unified structured logging
│       └── utils.py                    # Paths, config loader, and helpers
│
├── scripts/
│   ├── generate_data.py                # Scalable data generation CLI
│   ├── setup_hdfs.bat / .sh            # HDFS logical directory initialization
│   ├── upload_to_hdfs.py               # HDFS dataset staging CLI
│   ├── run_mapreduce.py                # MapReduce batch execution CLI
│   ├── run_spark.py                    # PySpark MLlib clustering CLI
│   ├── run_streaming.py                # Standalone streaming detector CLI
│   ├── seed_mongodb.py                 # Seeds MongoDB with historical results
│   ├── run_demo.py                     # Deterministic academic live demo
│   └── run_performance_experiment.py   # Empirical scalability benchmark
│
├── dashboard/
│   ├── app.py                          # Streamlit SOC dashboard application
│   ├── components.py                   # Reusable UI cards and widgets
│   └── queries.py                      # Data retrieval and chart abstractions
│
├── tests/                              # PyTest test suite (14 passing tests)
│   ├── test_generator.py
│   ├── test_bloom_filter.py
│   ├── test_detectors.py
│   ├── test_threat_score.py
│   ├── test_sliding_window.py
│   ├── test_mongodb.py
│   └── test_pipeline.py
│
├── docs/                               # Detailed documentation & viva guide
│   ├── architecture.md
│   ├── pipeline.md
│   ├── big_data_concepts.md
│   ├── detection_logic.md
│   └── demo_script.md
│
└── results/
    ├── mapreduce/                      # TSV and CSV MapReduce outputs
    ├── spark/                          # Cluster centroids and feature summaries
    ├── streaming/                      # Live threat alerts CSV exports
    ├── figures/                        # Scalability charts
    └── reports/                        # Empirical markdown/csv benchmarks
```

---

## 7. Setup & Installation

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Verify MongoDB Service
MongoDB Server is used for persistent alert storage. If using local native MongoDB (port 27017):
```powershell
# Verify MongoDB connection
python -c "from src.database.mongodb import MongoDBManager; print('MongoDB Status:', MongoDBManager().is_connected())"
```
*(Optional Docker alternative: `docker compose up -d`)*

---

## 8. Step-by-Step Execution Guide

### Step 1: Generate Telemetry Dataset
Generate synthetic network events (scalable up to 10M records):
```powershell
# Generate 100,000 events (creates data/generated/events_100000.csv and sample file)
python scripts/generate_data.py --events 100000
```

### Step 2: Stage Data to HDFS
Initialize HDFS logical namespaces and upload the dataset:
```powershell
# Create logical namespaces and upload
python scripts/upload_to_hdfs.py --input data/generated/events_100000.csv --dest /cyber-threat/raw/ --list
```

### Step 3: Execute Hadoop MapReduce Batch Analytics
Run all 4 MapReduce streaming jobs (Source IP counts, attack distribution, port frequencies, port diversity):
```powershell
python scripts/run_mapreduce.py
```
*Generated outputs saved in `results/mapreduce/`: `mapreduce_top_ips.csv`, `mapreduce_attack_counts.csv`, and TSVs.*

### Step 4: Execute Apache Spark Analytics & MLlib Clustering
Execute distributed feature aggregation, vector scaling, and K-Means clustering:
```powershell
python scripts/run_spark.py --k 4
```
*Generated outputs saved in `results/spark/`: `cluster_summary.csv`, `spark_clusters.csv`, and `spark_ip_features.csv`.*

### Step 5: Seed MongoDB Collections
Persist historical batch aggregates and reference alerts into MongoDB:
```powershell
python scripts/seed_mongodb.py
```

### Step 6: Launch Real-Time Streamlit Dashboard
Launch the SOC dashboard:
```powershell
streamlit run dashboard/app.py
```
Access the dashboard at `http://localhost:8501`.

### Step 7: Run Controlled Live Attack Simulation
In a separate terminal, execute the automated academic demonstration sequence:
```powershell
python scripts/run_demo.py --step-duration 5
```
Watch the Streamlit dashboard react in real-time as traffic spikes and alerts fire!

---

## 9. Real-Time Streaming Detection Details

### 5-Minute Sliding Window
- Maintains recent flow events in a timestamp-ordered deque.
- Automatically purges events older than 300 seconds.
- Computes flow velocity (events/s, packets/s, bytes/s) and connection rejection ratios.

### Probabilistic Bloom Filter
- Formulated with optimal bit capacity $m = -\frac{n \ln(p)}{(\ln 2)^2}$ and hash count $k = \frac{m}{n} \ln 2$.
- Tracks 1,000,000 IP addresses in only **1.17 MB of RAM** with a controlled 1% false-positive probability.
- Guarantees zero false negatives.

### Threat Scoring Formulation
$$\text{ThreatScore} = \begin{cases} 
0.70 \cdot \max(\text{DDoS}, \text{PortScan}, \text{Anomaly}) + 0.30 \cdot \text{Frequency} & \text{if attack active} \\
0.20 \cdot \text{Frequency} & \text{baseline}
\end{cases}$$
- `0.80 - 1.00`: **CRITICAL** (Volumetric flood attacks)
- `0.60 - 0.80`: **HIGH** (Port scan reconnaissance)
- `0.30 - 0.60`: **MEDIUM** (Covert channel anomalies)
- `0.00 - 0.30`: **LOW** (Safe enterprise flow)

---

## 10. Empirical Scalability Experiment

Run the automated benchmarking experiment:
```powershell
python scripts/run_performance_experiment.py --sizes 10000 50000 100000
```

### Empirical Throughput Results (Local Benchmark)

| Dataset Size (Events) | File Size (MB) | MapReduce Time (s) | MapReduce Throughput | Streaming Throughput |
| :--- | :--- | :--- | :--- | :--- |
| **10,000** | 0.86 MB | 0.15s | 67,815 ev/s | 46,233 ev/s |
| **50,000** | 4.29 MB | 0.23s | 221,698 ev/s | 44,343 ev/s |
| **100,000** | 8.58 MB | 0.29s | 342,971 ev/s | 48,471 ev/s |

*Throughput chart saved to `results/figures/scalability_throughput.png`.*

---

## 11. Automated Testing

Run the full unit and integration test suite:
```powershell
pytest tests/ -v
```
All **14 test cases pass**, covering event schemas, Bloom filters, sliding window eviction, detectors, scoring, MongoDB persistence, and end-to-end smoke tests.

---

## 12. Project Limitations & Future Work

### Limitations
1. In standalone development environments lacking full active multi-node YARN clusters, MapReduce and Spark run in local distributed mode (`local[*]`).
2. Telemetry is synthetically generated to strictly adhere to ethical guidelines without launching physical attacks on networks.

### Future Work
1. Integrate Apache Kafka as a persistent distributed message broker between the event producer and Spark Streaming.
2. Deploy Spark Streaming / Structured Streaming on a Kubernetes cluster.
3. Integrate graph analytics (GraphX) to map lateral movement and command-and-control (C2) botnet topologies.
