# Empirical Big Data Scalability & Throughput Evaluation

| Dataset Size (Events) | File Size (MB) | MapReduce Time (s) | MapReduce Throughput (ev/s) | Streaming Throughput (ev/s) |
| :--- | :--- | :--- | :--- | :--- |
| 10,000 | 0.86 MB | 0.147s | 67,814.6 | 46,232.6 |
| 50,000 | 4.29 MB | 0.226s | 221,698.2 | 44,343.3 |
| 100,000 | 8.58 MB | 0.292s | 342,971.2 | 48,471.4 |

### Observations
1. **Linear Scalability:** MapReduce processing scales near-linearly with input volume.
2. **High-Velocity Streaming:** Sliding window and Bloom Filter achieve tens of thousands of evaluations per second on a single thread.
3. **Bounded Memory:** Space-Saving heavy-hitters algorithm and Bloom filter bit arrays maintain constant memory footprint regardless of stream length.
