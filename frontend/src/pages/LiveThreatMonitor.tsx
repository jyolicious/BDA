import React from 'react';
import {
  Radio,
  Cpu,
  Layers,
  Filter,
  ShieldAlert,
  Clock,
  Sparkles,
  TrendingUp,
  Database,
  Search
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import { TelemetryPayload } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';

interface LiveThreatMonitorProps {
  telemetry: TelemetryPayload | null;
  onInvestigateIP: (ip: string) => void;
}

export const LiveThreatMonitor: React.FC<LiveThreatMonitorProps> = ({
  telemetry,
  onInvestigateIP,
}) => {
  const engine = telemetry?.engine || {
    events_processed: 0,
    events_per_second: 0,
    threats_detected: 0,
    critical_alerts: 0,
    mode: 'NORMAL',
    is_streaming: false,
  };

  const slidingWindow = telemetry?.sliding_window || {
    active_events: 0,
    active_ips: 0,
    window_duration_seconds: 300,
  };

  const bloom = telemetry?.bloom_filter || {
    capacity: 1000000,
    elements_added: 0,
    num_bits: 9585059,
    num_hash_functions: 7,
    fill_ratio: 0.0,
    current_fpp: 0.0,
    memory_usage_kb: 1170.0,
  };

  const trafficHistory = telemetry?.traffic_history || [];
  const recentAlerts = telemetry?.recent_alerts || [];
  const topSuspicious = telemetry?.top_suspicious_ips || [];

  return (
    <div className="space-y-6 font-mono">
      {/* Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wider flex items-center space-x-2">
            <Radio className="w-5 h-5 text-cyber-cyan animate-pulse" />
            <span>LIVE THREAT MONITOR &bull; STREAM TELEMETRY</span>
          </h2>
          <p className="text-xs text-cyber-muted mt-0.5">
            5-Minute rolling sliding window &bull; Space-Saving heavy hitters &bull; Sub-millisecond Bloom Filter membership testing
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs px-2.5 py-1 rounded bg-cyber-card border border-cyber-border text-cyber-cyan font-bold">
            WINDOW SIZE: 300s (5 MIN)
          </span>
        </div>
      </div>

      {/* Top 3 Stream Processing Telemetry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Card 1: 5-Minute Sliding Window */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cyber-border/60 pb-2 mb-3">
              <span className="text-xs font-bold text-cyber-cyan flex items-center">
                <Clock className="w-4 h-4 mr-1.5" />
                5-MINUTE ROLLING SLIDING WINDOW
              </span>
              <span className="text-[10px] bg-cyber-cyan/10 text-cyber-cyan px-1.5 py-0.5 rounded border border-cyber-cyan/30">
                ACTIVE DEQUE
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-cyber-muted">Events in Window:</span>
                <strong className="text-white text-base">{slidingWindow.active_events.toLocaleString()}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-cyber-muted">Active Unique Hosts:</span>
                <strong className="text-white text-base">{slidingWindow.active_ips.toLocaleString()}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-cyber-muted">Pruning Strategy:</span>
                <strong className="text-cyber-green">Deterministic FIFO (300s)</strong>
              </div>
            </div>
          </div>
          <p className="text-[10px] text-cyber-muted/80 mt-3 pt-2 border-t border-cyber-border/40">
            Calculates live flow rate, packet velocity, and port spread per host without unbounded memory growth.
          </p>
        </div>

        {/* Card 2: Probabilistic Bloom Filter */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cyber-border/60 pb-2 mb-3">
              <span className="text-xs font-bold text-cyber-cyan flex items-center">
                <Filter className="w-4 h-4 mr-1.5" />
                BLOOM FILTER (MEMBERSHIP TEST)
              </span>
              <span className="text-[10px] bg-cyber-green/10 text-cyber-green px-1.5 py-0.5 rounded border border-cyber-green/30">
                ZERO FALSE NEGATIVES
              </span>
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-cyber-muted">IPs Filtered:</span>
                <strong className="text-white">{bloom.elements_added.toLocaleString()}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-cyber-muted">Memory Allocated:</span>
                <strong className="text-cyber-cyan">{bloom.memory_usage_kb.toFixed(1)} KB</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-cyber-muted">Hash Functions (k):</span>
                <strong className="text-white">{bloom.num_hash_functions} (Kirsch-Mitzenmacher)</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-cyber-muted">Current FPP:</span>
                <strong className="text-cyber-green">{bloom.current_fpp.toFixed(6)}</strong>
              </div>
            </div>
          </div>

          <div className="mt-2 pt-2 border-t border-cyber-border/40">
            <div className="flex justify-between text-[10px] text-cyber-muted mb-1">
              <span>Bit Array Saturation</span>
              <span>{(bloom.fill_ratio * 100).toFixed(2)}%</span>
            </div>
            <div className="w-full bg-cyber-bg h-1.5 rounded overflow-hidden">
              <div
                className="bg-cyber-cyan h-full transition-all duration-300"
                style={{ width: `${Math.min(bloom.fill_ratio * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Card 3: Multi-Detector State */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cyber-border/60 pb-2 mb-3">
              <span className="text-xs font-bold text-cyber-cyan flex items-center">
                <Cpu className="w-4 h-4 mr-1.5" />
                STREAMING DETECTORS STATE
              </span>
              <span className="text-[10px] bg-cyber-card text-cyber-text px-1.5 py-0.5 rounded border border-cyber-border">
                ACTIVE
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-cyber-muted">1. Volumetric DDoS:</span>
                <span className="text-cyber-red font-bold">Rate Thresholds Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-cyber-muted">2. Port Reconnaissance:</span>
                <span className="text-cyber-amber font-bold">Port Entropy / Failure</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-cyber-muted">3. Statistical Anomaly:</span>
                <span className="text-cyber-cyan font-bold">Asymmetry &amp; Covert Ports</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-cyber-muted">Threat Scoring Engine:</span>
                <span className="text-white font-bold">Normalized [0.0 - 1.0]</span>
              </div>
            </div>
          </div>

          <p className="text-[10px] text-cyber-muted/80 mt-2 pt-2 border-t border-cyber-border/40">
            Configured in <code className="text-cyber-cyan">config/detection_rules.yaml</code>
          </p>
        </div>
      </div>

      {/* Live Stream Traffic Throughput Chart */}
      <div className="hud-card p-4 rounded-sm">
        <div className="flex items-center justify-between mb-3 border-b border-cyber-border/60 pb-2">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wider flex items-center">
              <TrendingUp className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              LIVE THROUGHPUT VISUALIZATION (EVENTS / SECOND)
            </h3>
            <p className="text-[11px] text-cyber-muted">
              Monitoring high-frequency packet bursts. Volumetric surge indicates active DDoS.
            </p>
          </div>
          <span className="text-xs text-cyber-cyan font-bold">
            CURRENT: {engine.events_per_second.toFixed(1)} EV/S
          </span>
        </div>

        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trafficHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="monitorTrafficGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#39D5FF" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#39D5FF" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="timestamp" stroke="#8291A8" fontSize={10} fontStyle="JetBrains Mono" />
              <YAxis stroke="#8291A8" fontSize={10} fontStyle="JetBrains Mono" />
              <Tooltip
                contentStyle={{ backgroundColor: '#101A2B', borderColor: '#1D2B40', borderRadius: '4px', fontSize: '11px', fontFamily: 'JetBrains Mono' }}
              />
              <Area
                type="monotone"
                dataKey="rate"
                stroke="#39D5FF"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#monitorTrafficGrad)"
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Grid: Live Alerts & Heavy Hitters */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Live Detected Threats Table */}
        <div className="hud-card p-4 rounded-sm flex flex-col">
          <div className="flex items-center justify-between mb-3 border-b border-cyber-border/60 pb-2">
            <h3 className="text-sm font-bold text-white tracking-wider flex items-center">
              <ShieldAlert className="w-4 h-4 mr-1.5 text-cyber-red" />
              STREAM DETECTOR ALERTS (RECENT 50)
            </h3>
            <span className="text-xs text-cyber-red font-bold">
              {recentAlerts.length} Recorded
            </span>
          </div>

          <div className="overflow-y-auto max-h-80 space-y-2">
            {recentAlerts.length > 0 ? (
              recentAlerts.map((alt, idx) => (
                <div
                  key={idx}
                  onClick={() => onInvestigateIP(alt.source_ip)}
                  className="p-3 bg-cyber-surface hover:bg-cyber-card border-l-4 border-cyber-red rounded cursor-pointer transition-colors text-xs space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <strong className="text-white">{alt.threat_type}</strong>
                      <span className="text-cyber-muted text-[10px]">{alt.timestamp.slice(11, 19)}</span>
                    </div>
                    <SeverityBadge severity={alt.severity} size="sm" />
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-cyber-cyan font-bold">{alt.source_ip}</span>
                    <span className="text-cyber-muted">Score: <strong className="text-white">{alt.threat_score.toFixed(2)}</strong></span>
                  </div>
                  <p className="text-[11px] text-cyber-muted/90 truncate">
                    {alt.detection_reason}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-center text-cyber-muted py-12 italic">
                No active threats detected. Run an attack in the Attack Simulator to test detector.
              </p>
            )}
          </div>
        </div>

        {/* Space-Saving Heavy-Hitters Table */}
        <div className="hud-card p-4 rounded-sm flex flex-col">
          <div className="flex items-center justify-between mb-3 border-b border-cyber-border/60 pb-2">
            <h3 className="text-sm font-bold text-white tracking-wider flex items-center">
              <Layers className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              HEAVY-HITTERS (SPACE-SAVING ALGORITHM)
            </h3>
            <span className="text-[10px] bg-cyber-card px-2 py-0.5 rounded border border-cyber-border text-cyber-muted">
              BOUNDED MEMORY O(k)
            </span>
          </div>

          <div className="overflow-x-auto flex-1 max-h-80">
            <table className="w-full text-left text-xs">
              <thead className="bg-cyber-surface text-[10px] text-cyber-muted uppercase border-b border-cyber-border">
                <tr>
                  <th className="p-2">Host IP</th>
                  <th className="p-2">Threat Score</th>
                  <th className="p-2">Severity</th>
                  <th className="p-2">Flow Volume</th>
                  <th className="p-2 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyber-border/40">
                {topSuspicious.slice(0, 10).map((host, idx) => (
                  <tr
                    key={idx}
                    onClick={() => onInvestigateIP(host.source_ip)}
                    className="hover:bg-cyber-surface/60 cursor-pointer transition-colors"
                  >
                    <td className="p-2 text-cyber-cyan font-bold hover:underline">
                      {host.source_ip}
                    </td>
                    <td className="p-2 text-white font-bold">
                      {host.threat_score.toFixed(2)}
                    </td>
                    <td className="p-2">
                      <SeverityBadge severity={host.severity} size="sm" />
                    </td>
                    <td className="p-2 text-cyber-muted">
                      {host.event_count.toLocaleString()}
                    </td>
                    <td className="p-2 text-right">
                      <span className="text-[10px] text-cyber-cyan hover:underline">&rarr;</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
