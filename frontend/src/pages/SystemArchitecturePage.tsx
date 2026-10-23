import React, { useState } from 'react';
import { Cpu, HardDrive, Database, Radio, Layers, Server, Sparkles, Filter, Clock, ShieldCheck, ExternalLink } from 'lucide-react';

interface ComponentDetail {
  id: string;
  name: string;
  category: 'BATCH' | 'STREAM' | 'STORAGE' | 'PRESENTATION';
  technology: string;
  role: string;
  input: string;
  output: string;
  status: 'ONLINE' | 'STANDBY';
  academicConcept: string;
}

export const SystemArchitecturePage: React.FC = () => {
  const [selectedComp, setSelectedComp] = useState<ComponentDetail>({
    id: 'spark',
    name: 'Apache Spark MLlib Clustering Engine',
    category: 'BATCH',
    technology: 'Apache Spark 4.2.0 (PySpark) + Java 17',
    role: 'Extracts 8-dimensional host behavior features, applies StandardScaler, and trains K-Means to identify behavioral archetypes.',
    input: 'Aggregated host network flow records from HDFS/CSV',
    output: 'Cluster centroids, host assignments, and interpretable cybersecurity profiles',
    status: 'ONLINE',
    academicConcept: 'Unsupervised Machine Learning & Distributed In-Memory Analytics',
  });

  const components: ComponentDetail[] = [
    {
      id: 'generator',
      name: 'Synthetic Network Event Generator',
      category: 'STREAM',
      technology: 'Python 3.13 Generator Engine',
      role: 'Generates multi-gigabyte synthetic network event telemetry adhering to 12-field schema across Normal, DDoS, PortScan, and Anomaly patterns.',
      input: 'Configurable random seeds and attack profiles',
      output: 'CSV Batches (up to 10M records) & continuous stream',
      status: 'ONLINE',
      academicConcept: 'Data Synthesis & Volume/Variety Generation',
    },
    {
      id: 'hdfs',
      name: 'HDFS Distributed File System',
      category: 'STORAGE',
      technology: 'HDFS / WebHDFS InsecureClient',
      role: 'Fault-tolerant distributed storage for raw and processed datasets across logical namespaces (/cyber-threat/raw, /features, /results).',
      input: 'Raw CSV network telemetry batches',
      output: 'Distributed blocks staged for parallel MapReduce and Spark jobs',
      status: 'ONLINE',
      academicConcept: 'Distributed Storage & Block Replication',
    },
    {
      id: 'mapreduce',
      name: 'Hadoop MapReduce Streaming Engine',
      category: 'BATCH',
      technology: 'Hadoop Streaming (Map -> Shuffle/Sort -> Reduce)',
      role: 'Executes 4 distributed aggregation jobs calculating source IP event counts, attack classification frequencies, and port activity.',
      input: 'HDFS raw telemetry datasets',
      output: 'results/mapreduce/ TSV and summary CSV reports',
      status: 'ONLINE',
      academicConcept: 'Distributed Parallel Processing & Map-Sort-Reduce Model',
    },
    {
      id: 'spark',
      name: 'Apache Spark MLlib Engine',
      category: 'BATCH',
      technology: 'Apache Spark 4.2.0 (PySpark)',
      role: 'Performs in-memory feature engineering (VectorAssembler + StandardScaler) and trains K-Means clustering (k=4) to discover threat profiles.',
      input: 'Host aggregated features from raw events',
      output: 'cluster_summary.csv & behavioral profile classifications',
      status: 'ONLINE',
      academicConcept: 'In-Memory Distributed Computation & Machine Learning',
    },
    {
      id: 'sliding-window',
      name: '5-Minute Rolling Sliding Window',
      category: 'STREAM',
      technology: 'Time-ordered Deque with FIFO Pruning',
      role: 'Maintains recent 300 seconds of telemetry per host. Computes event velocity, byte rates, packet rates, and failed connection ratios.',
      input: 'Continuous stream events',
      output: 'Real-time host rate metrics and connection drop stats',
      status: 'ONLINE',
      academicConcept: 'Stream Analytics & Sliding-Window Eviction',
    },
    {
      id: 'bloom-filter',
      name: 'Probabilistic Bloom Filter',
      category: 'STREAM',
      technology: 'Kirsch-Mitzenmacher Double-Hashing Bit Array',
      role: 'Tracks 1,000,000 source IPs in only 1.17 MB of RAM. Guarantees zero false negatives with bounded 1% false positive probability.',
      input: 'Incoming stream source IP addresses',
      output: 'O(k) Set membership testing response',
      status: 'ONLINE',
      academicConcept: 'Probabilistic Data Structures & Space Efficiency',
    },
    {
      id: 'threat-scorer',
      name: 'Explainable Threat Scoring Engine',
      category: 'STREAM',
      technology: 'Multi-Factor Heuristic Weighting Matrix',
      role: 'Combines DDoS traffic rate, port scan diversity, and anomaly exfiltration scores into normalized score [0.0 - 1.0] mapped to severity bands.',
      input: 'Host metrics from active sliding window',
      output: 'Normalized threat scores and SOC alerts',
      status: 'ONLINE',
      academicConcept: 'Cyber Threat Scoring & Attribution Formulation',
    },
    {
      id: 'mongodb',
      name: 'MongoDB NoSQL Storage',
      category: 'STORAGE',
      technology: 'MongoDB Server 8.0 / PyMongo',
      role: 'Stores threat alerts, raw events, and batch aggregates with compound indexes on timestamp, source_ip, and severity.',
      input: 'Triggered threat alert JSON documents',
      output: 'Indexed collections for sub-millisecond SOC queries',
      status: 'ONLINE',
      academicConcept: 'NoSQL Document Store & High-Volume Time-Series Indexing',
    },
    {
      id: 'fastapi',
      name: 'FastAPI REST & WebSocket Layer',
      category: 'PRESENTATION',
      technology: 'FastAPI + Uvicorn + WebSockets',
      role: 'Bridges Python distributed intelligence engine to the React frontend with 800ms WebSocket telemetry broadcast and REST triggers.',
      input: 'Engine telemetry snapshots and simulator commands',
      output: 'JSON WebSocket stream and REST endpoints',
      status: 'ONLINE',
      academicConcept: 'Low-Latency Full-Duplex WebSockets & Microservice Architecture',
    },
    {
      id: 'react-soc',
      name: 'SENTINEL React SOC Dashboard',
      category: 'PRESENTATION',
      technology: 'React 19 + TypeScript + Tailwind CSS',
      role: 'Interactive Security Operations Center visualization suite featuring real-time HUD widgets, radar sweeps, and simulation controls.',
      input: 'Real-time WebSocket telemetry stream',
      output: 'Visual SOC analytics, radar, and threat investigation view',
      status: 'ONLINE',
      academicConcept: 'Human-in-the-Loop Cybersecurity Observability',
    },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wider flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-cyber-cyan" />
            <span>LAMBDA ARCHITECTURE &bull; SYSTEM TOPOLOGY</span>
          </h2>
          <p className="text-xs text-cyber-muted mt-0.5">
            Unified Big Data architecture uniting distributed batch processing with sub-millisecond stream analytics.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Interactive Architecture Map (2 Columns) */}
        <div className="lg:col-span-2 hud-card p-5 rounded-sm space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-cyber-border pb-2 flex items-center justify-between">
            <span>INTERACTIVE COMPONENT SELECTOR</span>
            <span className="text-[10px] text-cyber-cyan">CLICK ANY COMPONENT TO INSPECT</span>
          </h3>

          <div className="space-y-4">
            {/* Top Source Layer */}
            <div className="flex justify-center">
              <button
                onClick={() => setSelectedComp(components.find((c) => c.id === 'generator')!)}
                className={`px-4 py-2 rounded border font-mono text-xs font-bold transition-all ${
                  selectedComp.id === 'generator'
                    ? 'bg-cyber-cyan text-black border-white shadow-cyan-glow'
                    : 'bg-cyber-surface hover:border-cyber-cyan text-white border-cyber-border'
                }`}
              >
                Network Event Telemetry (Generator &amp; Schema)
              </button>
            </div>

            {/* Split Paths Arrow */}
            <div className="flex justify-around text-cyber-muted text-xs font-bold">
              <span>&darr; HISTORICAL BATCH PATH</span>
              <span>&darr; REAL-TIME STREAMING PATH</span>
            </div>

            {/* Two Columns: Batch vs Streaming */}
            <div className="grid grid-cols-2 gap-4">
              {/* Batch Path Box */}
              <div className="p-3 bg-cyber-bg border border-cyber-border rounded space-y-2">
                <span className="text-[10px] text-cyber-muted uppercase font-bold block mb-1">
                  Historical Batch Layer
                </span>
                {components.filter((c) => c.category === 'BATCH' || c.id === 'hdfs').map((comp) => (
                  <button
                    key={comp.id}
                    onClick={() => setSelectedComp(comp)}
                    className={`w-full text-left p-2 rounded border text-xs transition-all block ${
                      selectedComp.id === comp.id
                        ? 'bg-cyber-cyan text-black font-bold border-white'
                        : 'bg-cyber-surface hover:bg-cyber-card border-cyber-border text-white'
                    }`}
                  >
                    <span className="font-bold block">{comp.name}</span>
                    <span className="text-[10px] text-cyber-muted block truncate">{comp.technology}</span>
                  </button>
                ))}
              </div>

              {/* Streaming Path Box */}
              <div className="p-3 bg-cyber-bg border border-cyber-border rounded space-y-2">
                <span className="text-[10px] text-cyber-muted uppercase font-bold block mb-1">
                  Speed / Stream Layer
                </span>
                {components.filter((c) => c.category === 'STREAM' && c.id !== 'generator').map((comp) => (
                  <button
                    key={comp.id}
                    onClick={() => setSelectedComp(comp)}
                    className={`w-full text-left p-2 rounded border text-xs transition-all block ${
                      selectedComp.id === comp.id
                        ? 'bg-cyber-cyan text-black font-bold border-white'
                        : 'bg-cyber-surface hover:bg-cyber-card border-cyber-border text-white'
                    }`}
                  >
                    <span className="font-bold block">{comp.name}</span>
                    <span className="text-[10px] text-cyber-muted block truncate">{comp.technology}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Convergence Layer: MongoDB -> FastAPI -> React */}
            <div className="pt-2 border-t border-cyber-border space-y-2">
              <span className="text-[10px] text-cyber-muted uppercase font-bold block text-center">
                Storage &bull; API &bull; Presentation Serving Layer
              </span>
              <div className="grid grid-cols-3 gap-2">
                {components.filter((c) => ['mongodb', 'fastapi', 'react-soc'].includes(c.id)).map((comp) => (
                  <button
                    key={comp.id}
                    onClick={() => setSelectedComp(comp)}
                    className={`p-2 rounded border text-center text-xs transition-all ${
                      selectedComp.id === comp.id
                        ? 'bg-cyber-cyan text-black font-bold border-white'
                        : 'bg-cyber-surface hover:bg-cyber-card border-cyber-border text-white'
                    }`}
                  >
                    <span className="font-bold block truncate">{comp.name.split(' ')[0]}</span>
                    <span className="text-[9px] text-cyber-muted block truncate">{comp.technology.split(' ')[0]}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Selected Component Inspector Panel (1 Column) */}
        <div className="hud-card p-5 rounded-sm flex flex-col justify-between">
          <div className="space-y-4 text-xs">
            <div className="border-b border-cyber-border pb-3">
              <span className="text-[10px] text-cyber-cyan uppercase font-bold tracking-wider">
                [{selectedComp.category} LAYER] COMPONENT SPECIFICATION
              </span>
              <h3 className="text-base font-bold text-white mt-1">{selectedComp.name}</h3>
              <span className="text-xs text-cyber-muted mt-0.5 block">{selectedComp.technology}</span>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-cyber-muted text-[10px] uppercase block">Academic Big Data Concept</span>
                <strong className="text-cyber-cyan block mt-0.5">{selectedComp.academicConcept}</strong>
              </div>

              <div>
                <span className="text-cyber-muted text-[10px] uppercase block">Architectural Role</span>
                <p className="text-cyber-text/90 mt-0.5 leading-relaxed bg-cyber-surface p-2.5 rounded border border-cyber-border">
                  {selectedComp.role}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="p-2 bg-cyber-bg rounded border border-cyber-border">
                  <span className="text-cyber-muted text-[10px] uppercase block">Input Artifact</span>
                  <span className="text-white text-[11px] font-bold">{selectedComp.input}</span>
                </div>
                <div className="p-2 bg-cyber-bg rounded border border-cyber-border">
                  <span className="text-cyber-muted text-[10px] uppercase block">Output Artifact</span>
                  <span className="text-cyber-green text-[11px] font-bold">{selectedComp.output}</span>
                </div>
              </div>

              <div className="flex justify-between items-center p-2.5 bg-cyber-surface rounded border border-cyber-border text-xs">
                <span className="text-cyber-muted">Operational State:</span>
                <span className="text-cyber-green font-bold flex items-center">
                  <span className="w-2 h-2 rounded-full bg-cyber-green mr-1.5 animate-pulse" />
                  {selectedComp.status}
                </span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-cyber-border text-[11px] text-cyber-muted">
            All components are fully implemented and running locally in Python &amp; React.
          </div>
        </div>
      </div>
    </div>
  );
};
