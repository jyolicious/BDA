# End-to-End Data Pipeline Specification

## 1. Data Ingestion & Storage Lifecycle

```
[Raw Event Generator]
        │
        ├──> CSV Batch Files (data/generated/events_<N>.csv)
        │           │
        │           ▼
        │    [HDFS Upload] ──> /cyber-threat/raw/
        │                           │
        │                           ├──> [MapReduce Jobs 1-4] ──> results/mapreduce/
        │                           │
        │                           └──> [Apache Spark MLlib]  ──> results/spark/
        │                                                              │
        │                                                              ▼
        │                                                      [MongoDB Database]
        │
        └──> [Streaming Producer]
                    │
                    ▼
          [Streaming Pipeline Engine]
             ├── Bloom Filter Membership Test
             ├── Space-Saving Heavy-Hitters Update
             ├── 5-Minute Sliding Window Maintenance
             ├── Rule-Based Detector Evaluation
             └── Composite Threat Scoring
                    │
                    ▼
          [Live MongoDB Threat Alerts] ──> [Streamlit Real-Time Dashboard]
```

---

## 2. Event Schema Specification

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `timestamp` | String (ISO 8601) | UTC timestamp of flow event | `2026-10-09T00:01:23` |
| `source_ip` | String (IPv4) | Transmitting client/attacker IP | `185.220.101.5` |
| `destination_ip` | String (IPv4) | Target host IP address | `10.0.0.5` |
| `source_port` | Integer | Ephemeral source port (1024-65535) | `45321` |
| `destination_port` | Integer | Destination service port (1-65535) | `80` |
| `protocol` | String | Transport protocol (`TCP`, `UDP`, `ICMP`) | `TCP` |
| `packet_count` | Integer | Flow packet count | `1250` |
| `bytes_sent` | Long Integer | Data transmitted by source (bytes) | `650000` |
| `bytes_received` | Long Integer | Data received by source (bytes) | `1200` |
| `duration_ms` | Integer | Flow connection duration in ms | `12` |
| `connection_status`| String | Flow state (`SUCCESS`, `FAILED`, `TIMEOUT`, `REJECTED`) | `SUCCESS` |
| `attack_label` | String | Ground-truth simulation label (`NORMAL`, `DDOS`, `PORT_SCAN`, `ANOMALOUS`) | `DDOS` |

---

## 3. MapReduce Batch Pipeline Jobs

1. **Job 1: Source IP Event Aggregation (`ip_count`)**
   - **Mapper:** Emits `(source_ip, 1)` for each flow line.
   - **Reducer:** Sums values per IP; outputs sorted frequency table.
2. **Job 2: Attack Classification Breakdown (`attack_freq`)**
   - **Mapper:** Emits `(attack_label, 1)`.
   - **Reducer:** Computes absolute counts and class proportions.
3. **Job 3: Destination Port Activity Profile (`port_activity`)**
   - **Mapper:** Emits `(destination_port, 1)`.
   - **Reducer:** Aggregates flow counts across probed ports.
4. **Job 4: Port Diversity per Host (`ip_ports`)**
   - **Mapper:** Emits `(source_ip, destination_port)`.
   - **Reducer:** Aggregates distinct ports probed per IP.

---

## 4. Spark MLlib Clustering Pipeline

1. **Host-Level Feature Engineering:**
   Aggregates raw flow events into 8 behavioral metrics per host:
   - Volume: `event_count`, `total_bytes_sent`, `total_bytes_received`
   - Flow characteristics: `avg_packet_count`, `avg_duration_ms`, `protocol_diversity`
   - Malicious indicators: `unique_dest_ports`, `failed_conn_count`
2. **Standardization:**
   Features are transformed with PySpark's `StandardScaler(withMean=True, withStd=True)`.
3. **K-Means Clustering:**
   Partitions hosts into $k=4$ behavioral clusters.
4. **Centroid Profile Interpretation:**
   Heuristic rules classify clusters into explainable roles:
   - **Volumetric Flood / DDoS Attack:** Characterized by hundreds of megabytes transmitted and high packets/flow.
   - **Reconnaissance / Port Scanner:** Characterized by >100 distinct probed ports and high failure rates.
   - **Covert Channel / Data Exfiltration:** Characterized by extreme byte asymmetry on non-standard ports.
   - **Normal Client Activity:** Characterized by balanced sent/received ratios and standard service ports.
