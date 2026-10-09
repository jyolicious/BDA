# Live Academic Demonstration Script

This document provides the exact sequence of steps, commands, and narrative talking points for presenting this project.

---

## 1. System Pre-Flight Check

Verify that all dependencies and database services are operational:
```powershell
# 1. Verify MongoDB is active
python -c "from src.database.mongodb import MongoDBManager; print('MongoDB Status:', MongoDBManager().is_connected())"

# 2. Run automated test suite (all 14 tests pass)
pytest tests/ -v
```

---

## 2. Phase 1: Data Generation & HDFS Distributed Staging

**Examiner Talking Point:**
> *"We begin by generating realistic synthetic network flow records. Each record contains 12 fields including flow duration, ports, and byte metrics. The data is uploaded to HDFS across our standard logical namespaces."*

**Commands:**
```powershell
# Generate 100,000 synthetic network events
python scripts/generate_data.py --events 100000

# Stage data into HDFS /cyber-threat/raw/ and verify
python scripts/upload_to_hdfs.py --input data/generated/events_100000.csv --dest /cyber-threat/raw/ --list
```

---

## 3. Phase 2: Historical Distributed Analytics (MapReduce & Spark)

**Examiner Talking Point:**
> *"For historical batch analytics, we execute Hadoop MapReduce to compute high-volume source IP rankings and attack distributions. Next, Apache Spark MLlib ingests the data, computes 8 behavioral metrics per host, scales them, and runs unsupervised K-Means clustering to discover distinct attack archetypes without supervision."*

**Commands:**
```powershell
# 1. Execute Hadoop MapReduce jobs
python scripts/run_mapreduce.py

# 2. Execute Apache Spark Analytics & MLlib Clustering
python scripts/run_spark.py --k 4

# 3. Seed MongoDB with historical aggregates and cluster profiles
python scripts/seed_mongodb.py
```

**Results to Show:**
- `results/mapreduce/mapreduce_top_ips.csv`
- `results/mapreduce/mapreduce_attack_counts.csv`
- `results/spark/cluster_summary.csv` (Show the interpretable behavioral profiles assigned to each cluster)

---

## 4. Phase 3: Real-Time Streaming Threat Detection (Live Interactive Demo)

**Examiner Talking Point:**
> *"Now we transition to the real-time streaming pipeline. We will launch the Streamlit dashboard and run the automated attack simulation sequence to witness the system detecting live attacks in real-time."*

**Commands:**
```powershell
# Launch the Streamlit dashboard in your browser
streamlit run dashboard/app.py
```

In a second terminal window (or directly from the Streamlit sidebar), run the demo orchestrator:
```powershell
python scripts/run_demo.py --step-duration 4
```

**What to Observe on Screen:**
1. **Phase 1 (Normal):** Baseline traffic flows at ~40 events/sec. Zero critical alerts.
2. **Phase 2 (DDoS Simulation):** Traffic rate visibly surges on the live chart to ~250 events/sec. The streaming sliding window detects excessive packet and byte rates. A **CRITICAL DDoS Alert** fires immediately, and the attacker IP is elevated to the Top Suspicious IPs table.
3. **Phase 3 (Normal Recovery):** Traffic stabilizes back to normal baseline.
4. **Phase 4 (Port Scan Simulation):** Scanner IP begins probing hundreds of ports with >90% connection drops. A **HIGH Port-Scan Alert** is triggered.
5. **Phase 5 (Covert Anomaly):** Massive exfiltration on covert port 4444 is flagged.
6. **Bloom Filter Widget:** Shows live unique IP count and verifies zero false negatives with bounded memory (<1.2 MB).

---

## 5. Phase 4: Big Data Scalability Evidence

**Examiner Talking Point:**
> *"To empirically prove scalability, we ran a performance benchmark across 10K, 50K, and 100K events. The pipeline demonstrated near-linear scaling, processing over 340,000 events/second in MapReduce and over 48,000 events/second in the streaming detector."*

**Commands / Artifacts to Show:**
```powershell
python scripts/run_performance_experiment.py
```
- Open and show: `results/reports/scalability_experiment.md`
- Open and show: `results/figures/scalability_throughput.png`
