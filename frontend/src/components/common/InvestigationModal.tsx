import React, { useEffect, useState } from 'react';
import { X, ShieldAlert, Cpu, Activity, Clock } from 'lucide-react';
import { api } from '../../services/api';
import { SeverityBadge } from './SeverityBadge';

interface InvestigationModalProps {
  ip: string | null;
  onClose: () => void;
}

export const InvestigationModal: React.FC<InvestigationModalProps> = ({ ip, onClose }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!ip) return;
    setLoading(true);
    api.getInvestigation(ip)
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [ip]);

  if (!ip) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-3xl hud-card hud-card-amber bg-cyber-card border border-cyber-border rounded-sm shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-cyber-border bg-cyber-surface">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-cyber-cyan/10 border border-cyber-cyan/30 rounded text-cyber-cyan">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-mono font-bold text-white tracking-wider">{ip}</h3>
                {data && <SeverityBadge severity={data.severity} size="sm" />}
              </div>
              <p className="text-xs text-cyber-muted font-mono">
                LAB SYNTHETIC SOURCE IP &bull; BEHAVIORAL THREAT INVESTIGATION
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-cyber-muted hover:text-white hover:bg-cyber-card transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 overflow-y-auto space-y-5 font-mono text-sm">
          {loading ? (
            <div className="py-16 text-center text-cyber-muted">
              <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-cyber-cyan" />
              <span>Querying host telemetry & active sliding window...</span>
            </div>
          ) : data ? (
            <>
              {/* Quick Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-cyber-surface p-3 rounded border border-cyber-border/70">
                  <span className="text-[10px] text-cyber-muted block">THREAT SCORE</span>
                  <span className="text-xl font-bold text-cyber-cyan">
                    {data.threat_score?.toFixed(2) || '0.00'}
                  </span>
                  <span className="text-[10px] text-cyber-muted block mt-0.5">Scale: 0.0 - 1.0</span>
                </div>
                <div className="bg-cyber-surface p-3 rounded border border-cyber-border/70">
                  <span className="text-[10px] text-cyber-muted block">TOTAL OBSERVED FLOWS</span>
                  <span className="text-xl font-bold text-white">
                    {data.total_observed_events?.toLocaleString() || 0}
                  </span>
                  <span className="text-[10px] text-cyber-muted block mt-0.5">Network Events</span>
                </div>
                <div className="bg-cyber-surface p-3 rounded border border-cyber-border/70">
                  <span className="text-[10px] text-cyber-muted block">BLOOM FILTER PRESENCE</span>
                  <span className="text-xl font-bold text-cyber-green">
                    {data.is_known_in_bloom_filter ? 'VERIFIED' : 'NOT FOUND'}
                  </span>
                  <span className="text-[10px] text-cyber-muted block mt-0.5">O(k) Hash Membership</span>
                </div>
                <div className="bg-cyber-surface p-3 rounded border border-cyber-border/70">
                  <span className="text-[10px] text-cyber-muted block">SEVERITY CLASSIFICATION</span>
                  <div className="mt-1">
                    <SeverityBadge severity={data.severity} size="sm" />
                  </div>
                </div>
              </div>

              {/* Detection Reasoning Box */}
              <div className="p-3.5 bg-cyber-bg border border-cyber-border/80 rounded">
                <div className="flex items-center space-x-2 text-cyber-amber text-xs font-semibold mb-1">
                  <Cpu className="w-4 h-4" />
                  <span>DETECTION ENGINE RATIONALE</span>
                </div>
                <p className="text-xs text-cyber-text/90 leading-relaxed">
                  {data.detection_reason || 'Flow behavior conformant with standard enterprise baseline.'}
                </p>
              </div>

              {/* Active Window Metrics */}
              {data.active_window_metrics && (
                <div>
                  <h4 className="text-xs font-bold text-cyber-cyan tracking-wider uppercase mb-2 flex items-center">
                    <Activity className="w-3.5 h-3.5 mr-1.5" />
                    5-Minute Rolling Window Telemetry
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2.5 text-xs bg-cyber-surface p-3 rounded border border-cyber-border/60">
                    <div>
                      <span className="text-cyber-muted block text-[10px]">EVENT RATE</span>
                      <strong className="text-white">{data.active_window_metrics.event_rate_per_sec} ev/s</strong>
                    </div>
                    <div>
                      <span className="text-cyber-muted block text-[10px]">BYTE VELOCITY</span>
                      <strong className="text-white">{(data.active_window_metrics.byte_rate_per_sec / 1024).toFixed(1)} KB/s</strong>
                    </div>
                    <div>
                      <span className="text-cyber-muted block text-[10px]">PACKET VELOCITY</span>
                      <strong className="text-white">{data.active_window_metrics.packet_rate_per_sec} pkts/s</strong>
                    </div>
                    <div>
                      <span className="text-cyber-muted block text-[10px]">PROBED PORTS</span>
                      <strong className="text-white">{data.active_window_metrics.unique_dest_ports} distinct</strong>
                    </div>
                    <div>
                      <span className="text-cyber-muted block text-[10px]">FAILED CONNECTIONS</span>
                      <strong className="text-cyber-red">{data.active_window_metrics.failed_connections} drops</strong>
                    </div>
                    <div>
                      <span className="text-cyber-muted block text-[10px]">FAILURE RATIO</span>
                      <strong className="text-cyber-amber">{(data.active_window_metrics.failed_ratio * 100).toFixed(1)}%</strong>
                    </div>
                  </div>
                </div>
              )}

              {/* Related Alert Incidents */}
              <div>
                <h4 className="text-xs font-bold text-cyber-cyan tracking-wider uppercase mb-2 flex items-center">
                  <Clock className="w-3.5 h-3.5 mr-1.5" />
                  Recent Triggered Alerts ({data.related_alerts?.length || 0})
                </h4>
                {data.related_alerts && data.related_alerts.length > 0 ? (
                  <div className="space-y-1.5 max-h-48 overflow-y-auto">
                    {data.related_alerts.map((alt: any, i: number) => (
                      <div
                        key={i}
                        className="p-2.5 bg-cyber-surface border-l-2 border-cyber-red rounded text-xs flex justify-between items-center"
                      >
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="text-white font-bold">{alt.threat_type}</span>
                            <span className="text-cyber-muted text-[10px]">{alt.timestamp}</span>
                          </div>
                          <p className="text-[11px] text-cyber-muted mt-0.5 truncate max-w-md">
                            {alt.detection_reason}
                          </p>
                        </div>
                        <SeverityBadge severity={alt.severity} size="sm" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-cyber-muted italic">No critical alerts recorded in MongoDB for this host.</p>
                )}
              </div>
            </>
          ) : (
            <div className="text-cyber-muted text-center py-8">Unable to fetch host intelligence.</div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 bg-cyber-surface border-t border-cyber-border flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-cyber-card border border-cyber-border text-white text-xs font-mono rounded hover:bg-cyber-border transition-colors"
          >
            Close Investigation
          </button>
        </div>
      </div>
    </div>
  );
};
