import React, { useState } from 'react';
import { Target, Search, ShieldAlert, Cpu, Activity, ExternalLink, Filter } from 'lucide-react';
import { TelemetryPayload, SuspiciousIP } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { RadarScanner } from '../components/common/RadarScanner';

interface ThreatInvestigationProps {
  telemetry: TelemetryPayload | null;
  onInvestigateIP: (ip: string) => void;
}

export const ThreatInvestigation: React.FC<ThreatInvestigationProps> = ({
  telemetry,
  onInvestigateIP,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const topSuspicious = telemetry?.top_suspicious_ips || [];
  const recentAlerts = telemetry?.recent_alerts || [];

  const filteredHosts = topSuspicious.filter((h) => {
    if (severityFilter !== 'ALL' && h.severity !== severityFilter) return false;
    if (searchTerm && !h.source_ip.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6 font-mono">
      {/* Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wider flex items-center space-x-2">
            <Target className="w-5 h-5 text-cyber-cyan" />
            <span>THREAT INTELLIGENCE &bull; HOST FORENSICS</span>
          </h2>
          <p className="text-xs text-cyber-muted mt-0.5">
            Detailed investigation profiles for high-risk IPs flagged by volumetric and reconnaissance detectors.
          </p>
        </div>
      </div>

      {/* Top Threat Radar & Attribution Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: Global Threat Radar */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between items-center">
          <div className="w-full flex items-center justify-between border-b border-cyber-border pb-2 mb-2">
            <span className="text-xs font-bold text-white uppercase flex items-center">
              <Cpu className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              THREAT RADAR
            </span>
            <span className="text-[10px] text-cyber-cyan bg-cyber-cyan/10 px-1.5 py-0.5 rounded border border-cyber-cyan/30">
              POLAR PROJECTION
            </span>
          </div>

          <RadarScanner alerts={recentAlerts} size={250} />

          <p className="text-[10px] text-cyber-muted text-center mt-2">
            Dynamic threat coordinates mapped from active sliding window flow velocity and port spread.
          </p>
        </div>

        {/* Right: Threat Attribution & Incident Summary (2 Columns) */}
        <div className="lg:col-span-2 hud-card p-4 rounded-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cyber-border pb-2 mb-3">
              <span className="text-xs font-bold text-white uppercase flex items-center">
                <ShieldAlert className="w-4 h-4 mr-1.5 text-cyber-amber" />
                AUTOMATED THREAT ATTRIBUTION SUMMARY
              </span>
              <span className="text-[10px] text-cyber-green bg-cyber-green/10 px-2 py-0.5 rounded border border-cyber-green/30">
                ACTIVE HEURISTICS
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="p-3 bg-cyber-surface rounded border border-cyber-border">
                <span className="text-[10px] text-cyber-muted block">CRITICAL THREATS</span>
                <strong className="text-xl text-cyber-red font-bold">
                  {recentAlerts.filter((a) => a.severity === 'CRITICAL').length}
                </strong>
                <span className="text-[10px] text-cyber-muted block">Volumetric Floods</span>
              </div>
              <div className="p-3 bg-cyber-surface rounded border border-cyber-border">
                <span className="text-[10px] text-cyber-muted block">RECON PROBES</span>
                <strong className="text-xl text-cyber-amber font-bold">
                  {recentAlerts.filter((a) => a.threat_type === 'PORT_SCAN').length}
                </strong>
                <span className="text-[10px] text-cyber-muted block">Port Sweeps</span>
              </div>
              <div className="p-3 bg-cyber-surface rounded border border-cyber-border">
                <span className="text-[10px] text-cyber-muted block">ANOMALIES</span>
                <strong className="text-xl text-cyber-cyan font-bold">
                  {recentAlerts.filter((a) => a.threat_type === 'ANOMALY').length}
                </strong>
                <span className="text-[10px] text-cyber-muted block">Covert Exfiltration</span>
              </div>
            </div>

            <p className="text-xs text-cyber-text/90 leading-relaxed bg-cyber-surface/60 p-3 rounded border border-cyber-border/70">
              The detection engine correlates <strong>real-time sliding window telemetry</strong> with historical <strong>Spark MLlib behavioral cluster centroids</strong> to compute normalized threat scores. Hosts exceeding critical thresholds trigger immediate SOC alerts and are automatically tracked in the Space-Saving heavy-hitters table.
            </p>
          </div>

          <div className="pt-3 border-t border-cyber-border text-xs text-cyber-muted flex justify-between">
            <span>DATABASE: <strong>MongoDB 8.0 Indexed Alerts</strong></span>
            <span>STORAGE: <strong>Persistent</strong></span>
          </div>
        </div>
      </div>

      {/* Filterable Suspicious Hosts Directory */}
      <div className="hud-card p-4 rounded-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 border-b border-cyber-border/60 pb-3 gap-3">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center">
              <Activity className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              SUSPICIOUS HOST DIRECTORY
            </h3>
            <p className="text-[11px] text-cyber-muted">
              Select any host to launch immediate deep-dive forensics.
            </p>
          </div>

          {/* Search & Filters */}
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-cyber-muted" />
              <input
                type="text"
                placeholder="Search IP..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1 bg-cyber-bg border border-cyber-border rounded text-xs text-white placeholder-cyber-muted/60 font-mono focus:border-cyber-cyan outline-none"
              />
            </div>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-2.5 py-1 bg-cyber-bg border border-cyber-border rounded text-xs text-white font-mono outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High Only</option>
              <option value="MEDIUM">Medium Only</option>
              <option value="LOW">Low Only</option>
            </select>
          </div>
        </div>

        {/* Directory Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-cyber-surface text-[10px] text-cyber-muted uppercase border-b border-cyber-border">
              <tr>
                <th className="p-3">Source IP Address</th>
                <th className="p-3">Threat Score</th>
                <th className="p-3">Severity Level</th>
                <th className="p-3">Threat Classification</th>
                <th className="p-3">Observed Flows</th>
                <th className="p-3">Last Activity</th>
                <th className="p-3 text-right">Forensic Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/40">
              {filteredHosts.length > 0 ? (
                filteredHosts.map((h, i) => (
                  <tr
                    key={i}
                    onClick={() => onInvestigateIP(h.source_ip)}
                    className="hover:bg-cyber-surface/60 cursor-pointer transition-colors group"
                  >
                    <td className="p-3 font-bold text-cyber-cyan group-hover:underline">
                      {h.source_ip}
                    </td>
                    <td className="p-3 text-white font-bold">
                      {h.threat_score.toFixed(2)}
                    </td>
                    <td className="p-3">
                      <SeverityBadge severity={h.severity} size="sm" />
                    </td>
                    <td className="p-3 text-white">
                      {Array.isArray(h.threat_types) ? h.threat_types.join(', ') : h.threat_types}
                    </td>
                    <td className="p-3 text-cyber-muted">
                      {h.event_count.toLocaleString()}
                    </td>
                    <td className="p-3 text-cyber-muted text-[11px]">
                      {h.last_seen || 'Active in Window'}
                    </td>
                    <td className="p-3 text-right">
                      <button className="px-2.5 py-1 rounded bg-cyber-card border border-cyber-border text-white text-[10px] group-hover:border-cyber-cyan group-hover:text-cyber-cyan transition-colors inline-flex items-center space-x-1">
                        <span>Investigate</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-cyber-muted italic">
                    No suspicious hosts matching current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
