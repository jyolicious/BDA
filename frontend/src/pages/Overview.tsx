import React, { useState } from 'react';
import {
  Activity,
  ShieldAlert,
  Flame,
  Radio,
  Users,
  Search,
  Filter,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  Layers,
  ExternalLink
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { TelemetryPayload, ThreatAlert, SuspiciousIP } from '../types';
import { KPICard } from '../components/common/KPICard';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { RadarScanner } from '../components/common/RadarScanner';

interface OverviewProps {
  telemetry: TelemetryPayload | null;
  onInvestigateIP: (ip: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const Overview: React.FC<OverviewProps> = ({
  telemetry,
  onInvestigateIP,
  onNavigateTab,
}) => {
  const [eventFilter, setEventFilter] = useState<'ALL' | 'NORMAL' | 'DDOS' | 'PORT_SCAN' | 'ANOMALOUS'>('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  // Fallbacks if telemetry not yet loaded
  const engine = telemetry?.engine || {
    events_processed: 0,
    events_per_second: 0,
    threats_detected: 0,
    critical_alerts: 0,
    is_streaming: false,
    mode: 'NORMAL',
    target_rate_eps: 40,
    uptime_seconds: 0,
  };

  const slidingWindow = telemetry?.sliding_window || {
    active_events: 0,
    active_ips: 0,
  };

  const trafficHistory = telemetry?.traffic_history || [];
  const recentAlerts = telemetry?.recent_alerts || [];
  const topSuspicious = telemetry?.top_suspicious_ips || [];
  const rawEvents = telemetry?.recent_events || [];

  // Filter raw events
  const filteredEvents = rawEvents.filter((ev) => {
    if (eventFilter !== 'ALL' && ev.attack_label !== eventFilter) return false;
    if (searchTerm && !ev.source_ip.includes(searchTerm) && !ev.destination_ip.includes(searchTerm)) return false;
    return true;
  });

  // Threat distribution chart data
  const dist = telemetry?.threat_distribution || { DDOS: 0, PORT_SCAN: 0, ANOMALY: 0, HIGH_VOLUME: 0 };
  const threatBarData = [
    { name: 'DDoS', count: dist.DDOS || 0, fill: '#FF4D67' },
    { name: 'Port Scan', count: dist.PORT_SCAN || 0, fill: '#FFBF69' },
    { name: 'Anomaly', count: dist.ANOMALY || 0, fill: '#39D5FF' },
    { name: 'High Vol', count: dist.HIGH_VOLUME || 0, fill: '#5B8CFF' },
  ];

  // Severity Donut Data
  const sevCounts = {
    CRITICAL: recentAlerts.filter((a) => a.severity === 'CRITICAL').length,
    HIGH: recentAlerts.filter((a) => a.severity === 'HIGH').length,
    MEDIUM: recentAlerts.filter((a) => a.severity === 'MEDIUM').length,
    LOW: recentAlerts.filter((a) => a.severity === 'LOW').length,
  };

  const severityPieData = [
    { name: 'Critical', value: sevCounts.CRITICAL || 1, color: '#FF4D67' },
    { name: 'High', value: sevCounts.HIGH || 1, color: '#FFBF69' },
    { name: 'Medium', value: sevCounts.MEDIUM || 1, color: '#39D5FF' },
    { name: 'Low', value: sevCounts.LOW || 2, color: '#35E6A1' },
  ];

  return (
    <div className="space-y-6">
      {/* Top SOC Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-3">
        <div>
          <h2 className="text-xl font-mono font-bold text-white tracking-wider flex items-center space-x-2">
            <span>SECURITY OPERATIONS CENTER</span>
            <span className="text-xs px-2 py-0.5 rounded bg-cyber-cyan/10 border border-cyber-cyan/30 text-cyber-cyan">
              TIER-1 INTELLIGENCE
            </span>
          </h2>
          <p className="text-xs font-mono text-cyber-muted mt-0.5">
            Real-time telemetry streams, probabilistic sliding-window detection, and distributed big data baselines.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onNavigateTab('simulator')}
            className="px-3.5 py-1.5 bg-cyber-red/20 border border-cyber-red/50 text-cyber-red hover:bg-cyber-red/30 rounded font-mono text-xs font-bold transition-all shadow-[0_0_15px_rgba(255,77,103,0.25)] flex items-center space-x-1.5"
          >
            <Flame className="w-3.5 h-3.5 fill-current" />
            <span>OPEN ATTACK SIMULATOR</span>
          </button>
          <button
            onClick={() => onNavigateTab('pipeline')}
            className="px-3 py-1.5 bg-cyber-card border border-cyber-border text-cyber-text hover:text-cyber-cyan rounded font-mono text-xs transition-colors flex items-center space-x-1"
          >
            <Layers className="w-3.5 h-3.5 mr-1" />
            <span>Big Data Jobs</span>
          </button>
        </div>
      </div>

      {/* 5 Headline KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
        <KPICard
          title="Total Events"
          value={engine.events_processed}
          subtitle="Processed by stream pipeline"
          icon={Activity}
          variant="cyan"
          trend="+Live"
        />
        <KPICard
          title="Events / Sec"
          value={engine.events_per_second.toFixed(1)}
          subtitle={`Target: ${engine.target_rate_eps || 40} ev/s`}
          icon={Radio}
          variant={engine.mode === 'DDOS' ? 'red' : 'green'}
          trend={engine.mode === 'DDOS' ? 'SPIKE' : undefined}
        />
        <KPICard
          title="Threats Flagged"
          value={engine.threats_detected}
          subtitle="Multi-detector triggers"
          icon={ShieldAlert}
          variant="amber"
        />
        <KPICard
          title="Critical Alerts"
          value={engine.critical_alerts}
          subtitle="Score >= 0.80 (Severity: CRIT)"
          icon={Flame}
          variant="red"
        />
        <KPICard
          title="Active Unique IPs"
          value={slidingWindow.active_ips}
          subtitle="Tracked in 5-min sliding window"
          icon={Users}
          variant="blue"
        />
      </div>

      {/* Primary Analytics Grid: Live Traffic Surge Chart & Radar/Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: Large Live Traffic Ingress Chart (2 Columns) */}
        <div className="lg:col-span-2 hud-card p-4 rounded-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3 border-b border-cyber-border/60 pb-2">
            <div>
              <h3 className="text-sm font-mono font-bold text-white tracking-wider flex items-center">
                <TrendingUp className="w-4 h-4 mr-1.5 text-cyber-cyan" />
                REAL-TIME EVENT RATE TELEMETRY (EVENTS / SEC)
              </h3>
              <p className="text-[11px] font-mono text-cyber-muted">
                Visibly surges during volumetric DDoS floods (Mode: <strong className="text-cyber-cyan">{engine.mode}</strong>)
              </p>
            </div>
            <div className="flex items-center space-x-2 font-mono text-[11px]">
              <span className="flex items-center text-cyber-cyan">
                <span className="w-2.5 h-2.5 rounded-full bg-cyber-cyan mr-1.5" />
                Ingress Rate
              </span>
              <span className="flex items-center text-cyber-muted">
                <span className="w-2.5 h-2.5 rounded-full bg-cyber-muted/40 mr-1.5" />
                Baseline
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            {trafficHistory.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trafficHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="trafficGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={engine.mode === 'DDOS' ? '#FF4D67' : '#39D5FF'} stopOpacity={0.4} />
                      <stop offset="95%" stopColor={engine.mode === 'DDOS' ? '#FF4D67' : '#39D5FF'} stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="timestamp" stroke="#8291A8" fontSize={10} fontStyle="JetBrains Mono" />
                  <YAxis stroke="#8291A8" fontSize={10} fontStyle="JetBrains Mono" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#101A2B', borderColor: '#1D2B40', borderRadius: '4px', fontSize: '11px', fontFamily: 'JetBrains Mono' }}
                    labelStyle={{ color: '#E7EEF8' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="rate"
                    stroke={engine.mode === 'DDOS' ? '#FF4D67' : '#39D5FF'}
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#trafficGradient)"
                    isAnimationActive={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-cyber-muted font-mono text-xs">
                Gathering live stream telemetry...
              </div>
            )}
          </div>

          <div className="mt-3 pt-2 border-t border-cyber-border/40 grid grid-cols-3 text-[11px] font-mono text-cyber-muted">
            <div>CURRENT RATE: <strong className="text-white">{engine.events_per_second.toFixed(1)} ev/s</strong></div>
            <div>SLIDING WINDOW: <strong className="text-cyber-cyan">{slidingWindow.active_events.toLocaleString()} events</strong></div>
            <div>STATUS: <strong className={engine.mode === 'DDOS' ? 'text-cyber-red animate-pulse' : 'text-cyber-green'}>{engine.mode === 'DDOS' ? 'VOLUMETRIC SURGE' : 'STEADY BASELINE'}</strong></div>
          </div>
        </div>

        {/* Right: Radar Scanning & Severity Breakdown (1 Column) */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2 border-b border-cyber-border/60 pb-2">
            <h3 className="text-xs font-mono font-bold text-white tracking-wider flex items-center">
              <Cpu className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              GLOBAL THREAT SCANNER
            </h3>
            <span className="text-[10px] font-mono text-cyber-cyan bg-cyber-cyan/10 px-1.5 py-0.5 rounded">
              360° SWEEP
            </span>
          </div>

          {/* Radar Screen from Reference UI */}
          <div className="flex-1 flex items-center justify-center">
            <RadarScanner alerts={recentAlerts} size={230} />
          </div>

          {/* Compact Threat Category Distribution Bar */}
          <div className="mt-3 pt-2 border-t border-cyber-border/60">
            <div className="text-[10px] font-mono text-cyber-muted uppercase mb-1.5 flex justify-between">
              <span>Category Distribution</span>
              <span className="text-cyber-cyan">{recentAlerts.length} Total Alerts</span>
            </div>
            <div className="h-16 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={threatBarData} layout="vertical" margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" stroke="#8291A8" fontSize={9} fontStyle="JetBrains Mono" width={60} />
                  <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                    {threatBarData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Grid: Top Suspicious IPs & Live Flow Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Top Suspicious IPs Table */}
        <div className="hud-card p-4 rounded-sm flex flex-col">
          <div className="flex items-center justify-between mb-3 border-b border-cyber-border/60 pb-2">
            <div>
              <h3 className="text-sm font-mono font-bold text-white tracking-wider flex items-center">
                <ShieldAlert className="w-4 h-4 mr-1.5 text-cyber-amber" />
                TOP SUSPICIOUS SOURCE IPS
              </h3>
              <p className="text-[11px] font-mono text-cyber-muted">
                Ranked by composite threat score $[0.0 - 1.0]$. Click any host to inspect telemetry.
              </p>
            </div>
            <button
              onClick={() => onNavigateTab('threat-intel')}
              className="text-xs font-mono text-cyber-cyan hover:underline flex items-center"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </button>
          </div>

          <div className="overflow-x-auto flex-1 max-h-72">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-cyber-surface/90 text-[10px] text-cyber-muted uppercase sticky top-0 border-b border-cyber-border">
                <tr>
                  <th className="p-2">Source IP</th>
                  <th className="p-2">Score</th>
                  <th className="p-2">Severity</th>
                  <th className="p-2">Flows</th>
                  <th className="p-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyber-border/40">
                {topSuspicious.length > 0 ? (
                  topSuspicious.slice(0, 7).map((host, idx) => (
                    <tr
                      key={idx}
                      onClick={() => onInvestigateIP(host.source_ip)}
                      className="hover:bg-cyber-surface/60 cursor-pointer transition-colors group"
                    >
                      <td className="p-2 font-bold text-cyber-cyan group-hover:underline">
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
                        <span className="text-[10px] px-2 py-0.5 rounded bg-cyber-card border border-cyber-border group-hover:border-cyber-cyan text-cyber-text">
                          Inspect &rarr;
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="p-4 text-center text-cyber-muted italic">
                      No anomalous hosts currently flagged.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Network Event Stream Feed */}
        <div className="hud-card p-4 rounded-sm flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3 border-b border-cyber-border/60 pb-2 gap-2">
            <div>
              <h3 className="text-sm font-mono font-bold text-white tracking-wider flex items-center">
                <Radio className="w-4 h-4 mr-1.5 text-cyber-cyan" />
                LIVE NETWORK EVENT FEED
              </h3>
              <p className="text-[11px] font-mono text-cyber-muted">
                Sub-millisecond flow telemetry arriving from event generator
              </p>
            </div>
            {/* Filter pills */}
            <div className="flex items-center space-x-1 font-mono text-[10px]">
              {(['ALL', 'NORMAL', 'DDOS', 'PORT_SCAN'] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setEventFilter(mode)}
                  className={`px-2 py-0.5 rounded border transition-colors ${
                    eventFilter === mode
                      ? 'bg-cyber-cyan/20 border-cyber-cyan text-cyber-cyan font-bold'
                      : 'bg-cyber-card border-cyber-border text-cyber-muted hover:text-white'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto flex-1 max-h-72 divide-y divide-cyber-border/40 font-mono text-xs">
            {filteredEvents.length > 0 ? (
              filteredEvents.slice(0, 8).map((ev, i) => (
                <div
                  key={i}
                  className="py-2 px-1.5 flex items-center justify-between hover:bg-cyber-surface/40 transition-colors text-[11px]"
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-cyber-muted text-[10px]">{ev.timestamp.slice(11, 19)}</span>
                    <span className="px-1.5 py-0.2 rounded bg-cyber-card border border-cyber-border text-white text-[10px]">
                      {ev.protocol}
                    </span>
                    <span
                      onClick={() => onInvestigateIP(ev.source_ip)}
                      className="text-cyber-cyan font-bold hover:underline cursor-pointer"
                    >
                      {ev.source_ip}:{ev.source_port}
                    </span>
                    <span className="text-cyber-muted">&rarr;</span>
                    <span className="text-white">
                      {ev.destination_ip}:{ev.destination_port}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-cyber-muted text-[10px]">
                      {(ev.bytes_sent / 1024).toFixed(1)} KB
                    </span>
                    <span
                      className={`text-[10px] font-bold px-1.5 rounded ${
                        ev.attack_label === 'DDOS'
                          ? 'bg-cyber-red/20 text-cyber-red border border-cyber-red/30'
                          : ev.attack_label === 'PORT_SCAN'
                          ? 'bg-cyber-amber/20 text-cyber-amber border border-cyber-amber/30'
                          : 'bg-cyber-green/10 text-cyber-green'
                      }`}
                    >
                      {ev.attack_label}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-cyber-muted italic">
                Awaiting telemetry events... Start stream above.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
