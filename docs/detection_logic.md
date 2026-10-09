# Cyber Threat Detection Logic & Scoring Formulations

## 1. Detector 1: Volumetric DDoS Attack Detection

### Behavioral Characteristics
- Massive volume of packets and bytes transmitted per unit time.
- Highly concentrated destination target ports (e.g. port 80 or 443).
- Low flow duration ($1-25$ ms).

### Mathematical Rules
Let $W$ be the active sliding window (5 minutes) and host $h$ have $N$ events:
1. **Event Rate:** $R_e = \frac{N}{\Delta t} \ge 15.0 \text{ events/sec}$
2. **Packet Rate:** $R_p = \frac{\sum \text{packets}}{\Delta t} \ge 300.0 \text{ pkts/sec}$
3. **Byte Rate:** $R_b = \frac{\sum \text{bytes}}{\Delta t} \ge 150,000 \text{ bytes/sec}$
4. **Port Concentration Factor:** $C_p = 1.0 \text{ if } |\text{UniquePorts}| \le 3 \text{ else } 0.5$

$$\text{TrafficScore} = C_p \cdot \left[ 0.4 \cdot \min\left(\frac{R_e}{2 R_e^*}, 1\right) + 0.3 \cdot \min\left(\frac{R_b}{2 R_b^*}, 1\right) + 0.3 \cdot \min\left(\frac{R_p}{2 R_p^*}, 1\right) \right]$$

---

## 2. Detector 2: Port Scan / Reconnaissance Detection

### Behavioral Characteristics
- Probing large numbers of distinct destination ports in rapid succession.
- High connection failure ratio (SYN requests answered with RST/Timeout/Rejection).
- Small byte payloads (TCP SYN flags only).

### Mathematical Rules
1. **Unique Ports:** $P_u = |\text{UniquePorts}(h)| \ge 15$
2. **Failure Ratio:** $F_r = \frac{N_{\text{failed}}}{N} \ge 0.50 \quad (50\%)$
3. **Minimum Volume:** $N \ge 20$

$$\text{PortScanScore} = 0.6 \cdot \min\left(\frac{P_u}{30}, 1\right) + 0.4 \cdot \min\left(\frac{F_r}{0.8}, 1\right)$$

---

## 3. Detector 3: Statistical Anomaly & Data Exfiltration Detection

### Behavioral Characteristics
- Covert communication over non-standard / malicious service ports (4444, 6667, 1337, 31337).
- Extreme data exfiltration asymmetry: bytes transmitted drastically exceed bytes received.

### Mathematical Rules
$$\text{AsymmetryRatio} = \frac{\text{BytesSent}}{\max(\text{BytesReceived}, 1)} \ge 10.0$$

$$\text{AnomalyScore} = 0.6 \cdot \mathbb{I}(\text{BytesSent} > 250\text{KB} \land \text{Asymmetry} \ge 10) + 0.4 \cdot \mathbb{I}(\text{Port} \in \text{UnusualPorts})$$

---

## 4. Explainable Composite Threat Scoring Formulation

The composite threat score is normalized in the range $[0.0, 1.0]$:

$$\text{MaxAttack} = \max(\text{TrafficScore}, \text{PortScanScore}, \text{AnomalyScore})$$

$$\text{ThreatScore} = \begin{cases} 
0.70 \cdot \text{MaxAttack} + 0.30 \cdot \text{FrequencyScore} & \text{if } \text{MaxAttack} > 0 \\
0.20 \cdot \text{FrequencyScore} & \text{otherwise}
\end{cases}$$

### Severity Banding
- **$0.80 \le \text{ThreatScore} \le 1.00$:** $\rightarrow$ `CRITICAL` (Active volumetric DDoS or high-consequence attack)
- **$0.60 \le \text{ThreatScore} < 0.80$:** $\rightarrow$ `HIGH` (Active port scanning or covert exfiltration)
- **$0.30 \le \text{ThreatScore} < 0.60$:** $\rightarrow$ `MEDIUM` (Suspicious volume or unusual port traffic)
- **$0.00 \le \text{ThreatScore} < 0.30$:** $\rightarrow$ `LOW` (Routine enterprise telemetry)
