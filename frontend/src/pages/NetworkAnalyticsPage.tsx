import React, { useEffect, useState } from 'react';
import { BarChart3, PieChart, Sparkles, Cpu, Layers, Database, RefreshCw, HardDrive } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { api } from '../services/api';
import { SparkClusterSummary } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';

export const NetworkAnalyticsPage: React.FC = () => {
  const [mrData, setMrData] = useState<any>(null);
  const [sparkData, setSparkData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadData = () => {
    setLoading(true);
    Promise.all([api.getMapReduceAnalytics(), api.getSparkAnalytics()])
      .then(([mr, spark]) => {
        setMrData(mr);
        setSparkData(spark);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const attackChartData = mrData?.attack_counts?.map((item: any) => ({
    name: item.attack_type,
    count: parseInt(item.event_count, 10),
    percentage: item.percentage,
    fill: item.attack_type === 'DDOS' ? '#FF4D67' : (item.attack_type === 'PORT_SCAN' ? '#FFBF69' : (item.attack_type === 'ANOMALOUS' ? '#39D5FF' : '#35E6A1'))
  })) || [];

  return (
    <div className="space-y-6 font-mono">
      {/* Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wider flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-cyber-cyan" />
            <span>NETWORK ANALYTICS &bull; HISTORICAL BATCH RESULTS</span>
          </h2>
          <p className="text-xs text-cyber-muted mt-0.5">
            Distributed MapReduce batch aggregations and Apache Spark MLlib unsupervised clustering outputs.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="px-3 py-1.5 bg-cyber-card border border-cyber-border text-white text-xs hover:border-cyber-cyan rounded flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyber-cyan' : ''}`} />
          <span>Reload Analytics</span>
        </button>
      </div>

      {/* Section 1: Apache Spark MLlib K-Means Host Behavioral Clustering */}
      <div className="hud-card p-5 rounded-sm space-y-4">
        <div className="flex items-center justify-between border-b border-cyber-border pb-2">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center">
              <Sparkles className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              APACHE SPARK MLlib K-MEANS BEHAVIORAL CLUSTERING
            </h3>
            <p className="text-[11px] text-cyber-muted">
              Standardized 8 host numerical features &bull; Model: Spark MLlib KMeans (k=4, maxIter=30)
            </p>
          </div>
          <span className="text-[10px] text-cyber-green bg-cyber-green/10 border border-cyber-green/30 px-2 py-0.5 rounded font-bold">
            MLlib CLUSTERS PERSISTED
          </span>
        </div>

        {/* Cluster Centroids Summary Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-cyber-surface text-[10px] text-cyber-muted uppercase border-b border-cyber-border">
              <tr>
                <th className="p-2.5">Cluster ID</th>
                <th className="p-2.5">Hosts</th>
                <th className="p-2.5">Assigned Behavioral Profile</th>
                <th className="p-2.5">Severity</th>
                <th className="p-2.5">Mean Sent (Bytes)</th>
                <th className="p-2.5">Mean Unique Ports</th>
                <th className="p-2.5">Mean Drops</th>
                <th className="p-2.5">Detection Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/40">
              {sparkData?.cluster_summary && sparkData.cluster_summary.length > 0 ? (
                sparkData.cluster_summary.map((row: SparkClusterSummary, idx: number) => (
                  <tr key={idx} className="hover:bg-cyber-surface/60 transition-colors">
                    <td className="p-2.5 font-bold text-cyber-cyan">Cluster {row.cluster}</td>
                    <td className="p-2.5 text-white font-bold">{row.host_count} hosts</td>
                    <td className="p-2.5 font-semibold text-white">{row.assigned_profile}</td>
                    <td className="p-2.5">
                      <SeverityBadge severity={row.threat_severity} size="sm" />
                    </td>
                    <td className="p-2.5 text-cyber-cyan font-bold">
                      {(row.mean_bytes_sent / 1024).toFixed(1)} KB
                    </td>
                    <td className="p-2.5 text-white">{row.mean_unique_ports.toFixed(1)}</td>
                    <td className="p-2.5 text-cyber-red font-bold">{row.mean_failed_conns.toFixed(1)}</td>
                    <td className="p-2.5 text-cyber-muted text-[11px] max-w-xs truncate">
                      {row.detection_rationale}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-cyber-muted italic">
                    Spark clustering results not found. Run Spark from the Big Data Pipeline page.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 2: Hadoop MapReduce Jobs 1 & 2 Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* MapReduce Job 2: Attack Type Frequency Distribution */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cyber-border pb-2 mb-3">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                <Cpu className="w-4 h-4 mr-1.5 text-cyber-cyan" />
                MAPREDUCE JOB 2: ATTACK CLASSIFICATION
              </h3>
              <span className="text-[10px] text-cyber-muted">results/mapreduce/</span>
            </div>

            <div className="h-52 w-full">
              {attackChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={attackChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                    <XAxis dataKey="name" stroke="#8291A8" fontSize={10} fontStyle="JetBrains Mono" />
                    <YAxis stroke="#8291A8" fontSize={10} fontStyle="JetBrains Mono" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#101A2B', borderColor: '#1D2B40', borderRadius: '4px', fontSize: '11px', fontFamily: 'JetBrains Mono' }}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {attackChartData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-cyber-muted italic text-xs">
                  Awaiting MapReduce Job 2 outputs...
                </div>
              )}
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-cyber-border/40 text-xs text-cyber-muted flex justify-between">
            <span>MAPPER: <code>(attack_label, 1)</code></span>
            <span>REDUCER: <code>sum(counts)</code></span>
          </div>
        </div>

        {/* MapReduce Job 1: High Volume Source IPs */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cyber-border pb-2 mb-3">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                <HardDrive className="w-4 h-4 mr-1.5 text-cyber-cyan" />
                MAPREDUCE JOB 1: TOP SOURCE IPS
              </h3>
              <span className="text-[10px] text-cyber-muted">results/mapreduce/</span>
            </div>

            <div className="overflow-y-auto max-h-52">
              <table className="w-full text-left text-xs">
                <thead className="bg-cyber-surface text-[10px] text-cyber-muted uppercase border-b border-cyber-border">
                  <tr>
                    <th className="p-2">Rank</th>
                    <th className="p-2">Source IP</th>
                    <th className="p-2">Total Events</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cyber-border/40">
                  {mrData?.top_ips && mrData.top_ips.length > 0 ? (
                    mrData.top_ips.slice(0, 8).map((item: any, i: number) => (
                      <tr key={i} className="hover:bg-cyber-surface/60">
                        <td className="p-2 text-cyber-muted">#{item.volume_rank || i + 1}</td>
                        <td className="p-2 font-bold text-cyber-cyan">{item.source_ip}</td>
                        <td className="p-2 text-white font-mono">{parseInt(item.event_count, 10).toLocaleString()}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={3} className="p-4 text-center text-cyber-muted italic">
                        MapReduce Top IPs data pending execution.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-cyber-border/40 text-xs text-cyber-muted flex justify-between">
            <span>MAPPER: <code>(source_ip, 1)</code></span>
            <span>REDUCER: <code>sum(counts)</code></span>
          </div>
        </div>
      </div>
    </div>
  );
};
