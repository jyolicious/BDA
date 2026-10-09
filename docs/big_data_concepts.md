# Big Data Concepts & Academic Viva Preparation

This document maps theoretical Big Data concepts to their concrete software implementations in this project.

---

## 1. The 5 V's of Big Data

| Big Data Dimension | Manifestation in this Project | Software Implementation |
| :--- | :--- | :--- |
| **Volume** | Datasets spanning millions of network flow records exceeding memory limits. | `scripts/generate_data.py` (chunked generator up to 10M events), HDFS logical staging. |
| **Velocity** | Network packets arriving at tens of thousands of events per second requiring real-time response. | `src/streaming/event_producer.py`, `src/streaming/pipeline.py` (sub-millisecond evaluation). |
| **Variety** | Multi-dimensional telemetry combining connection states, ports, protocols, byte sizes, and timestamps. | Canonical `NetworkEvent` schema (`src/data/schema.py`) used across CSV, DataFrames, JSON, and MongoDB documents. |
| **Veracity** | Filtering false positives and validating ambiguous traffic behavior using probabilistic methods. | `BloomFilter` (no false negatives), `ThreatScorer` multi-factor weighting. |
| **Value** | Converting high-volume unstructured network noise into actionable threat defense intelligence. | Real-time threat alerts, ranked suspicious IP tables, and cluster behavioral profiles. |

---

## 2. Distributed Storage: HDFS (Hadoop Distributed File System)
- **Concept:** Fault-tolerant, distributed file storage splitting massive datasets into distributed blocks across cluster DataNodes.
- **Implementation in Project:** `src/hdfs/hdfs_manager.py` implements complete HDFS lifecycle management:
  - Connects to WebHDFS endpoints (`http://localhost:9870`).
  - Manages logical directories: `/cyber-threat/raw`, `/cyber-threat/processed`, `/cyber-threat/features`, `/cyber-threat/results`.
  - Transparent fallback architecture ensuring identical logical HDFS path structures during local standalone operations.

---

## 3. Distributed Computation: Hadoop MapReduce
- **Concept:** Distributed parallel processing framework dividing computations into independent `Map` (filtering/sorting) and `Reduce` (summarizing/aggregating) phases.
- **Implementation in Project:**
  - `src/mapreduce/mapper.py`: Emits `<key>\t<value>` pairs from standard input.
  - Shuffle & Sort Phase: Partitions and sorts intermediate keys.
  - `src/mapreduce/reducer.py`: Streaming aggregation per key.
  - 4 production jobs: Source IP event counting, attack category distribution, port frequency analysis, and IP port diversity.

---

## 4. In-Memory Distributed Analytics: Apache Spark & MLlib
- **Concept:** Resilient Distributed Datasets (RDDs) and DataFrames providing 10x-100x faster in-memory analytics than disk-bound MapReduce.
- **Implementation in Project:**
  - `src/spark/spark_session.py`: Cluster configuration and PySpark runtime setup.
  - `src/spark/aggregation.py`: Distributed grouping and aggregation over millions of records.
  - `src/spark/feature_engineering.py`: `VectorAssembler` and `StandardScaler`.
  - `src/spark/clustering.py`: MLlib `KMeans` algorithm discovering latent behavioral profiles.

---

## 5. Streaming Analytics: Sliding Window Processing
- **Concept:** Bounded temporal evaluation over continuous data streams to identify trends without maintaining infinite history.
- **Implementation in Project:** `src/streaming/sliding_window.py` maintains a 5-minute rolling window with active event deques and deterministic eviction of expired telemetry.

---

## 6. Probabilistic Data Structures: Bloom Filter
- **Concept:** Space-efficient bit array allowing $O(k)$ membership testing with zero false negatives and bounded false positives.
- **Implementation in Project:** `src/streaming/bloom_filter.py` uses optimal bit sizing ($m$) and double-hashing ($k$ hashes) to track millions of seen IPs in mere kilobytes of RAM.

---

## 7. Streaming Heavy-Hitters: Space-Saving Algorithm
- **Concept:** Fixed-memory streaming frequency estimation tracking dominant items with guaranteed error bounds.
- **Implementation in Project:** `src/streaming/frequent_items.py` maintains top-K heavy hitters in $O(1)$ update time and $O(K)$ bounded memory.

---

## 8. NoSQL Database: MongoDB
- **Concept:** High-throughput document-oriented storage for semi-structured time-series alerts and schema-flexible threat logs.
- **Implementation in Project:** `src/database/mongodb.py` stores threat alerts with compound indexes on `(timestamp, source_ip, severity, threat_type)` enabling low-latency real-time queries.
