import React, { useEffect, useState } from 'react';
import { Play, Square, Bell, Clock, Activity, ShieldCheck, AlertTriangle } from 'lucide-react';
import { ThreatAlert } from '../../types';

interface NavbarProps {
  pageTitle: string;
  isStreaming: boolean;
  onToggleStream: () => void;
  recentAlerts: ThreatAlert[];
  onOpenAlert: (alert: ThreatAlert) => void;
  activeMode: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  pageTitle,
  isStreaming,
  onToggleStream,
  recentAlerts,
  onOpenAlert,
  activeMode,
}) => {
  const [timeUtc, setTimeUtc] = useState<string>('');
  const [timeLocal, setTimeLocal] = useState<string>('');
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    const updateClocks = () => {
      const now = new Date();
      setTimeUtc(now.toUTCString().slice(17, 25) + ' UTC');
      setTimeLocal(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateClocks();
    const interval = setInterval(updateClocks, 1000);
    return () => clearInterval(interval);
  }, []);

  const criticalCount = recentAlerts.filter((a) => a.severity === 'CRITICAL').length;

  return (
    <header className="h-16 bg-cyber-surface/90 backdrop-blur-md border-b border-cyber-border px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Title & Breadcrumbs */}
      <div className="flex items-center space-x-3">
        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-mono text-cyber-muted uppercase">SOC CONSOLE &bull;</span>
            <span className="text-[11px] font-mono text-cyber-cyan uppercase">{pageTitle}</span>
          </div>
          <h1 className="text-base font-mono font-bold tracking-wider text-white">
            {pageTitle}
          </h1>
        </div>
      </div>

      {/* Center/Right Status & Controls */}
      <div className="flex items-center space-x-4">
        {/* Live Stream Pulse Badge */}
        {isStreaming ? (
          <div className="flex items-center space-x-2 bg-cyber-cyan/10 border border-cyber-cyan/40 px-3 py-1 rounded text-cyber-cyan font-mono text-xs shadow-cyan-glow">
            <span className="w-2 h-2 rounded-full bg-cyber-cyan animate-ping" />
            <span className="font-bold tracking-widest">LIVE STREAMING</span>
            <span className="text-[10px] bg-cyber-card px-1.5 py-0.5 rounded text-white border border-cyber-border font-semibold">
              {activeMode}
            </span>
          </div>
        ) : (
          <div className="flex items-center space-x-1.5 bg-cyber-card border border-cyber-border px-3 py-1 rounded text-cyber-muted font-mono text-xs">
            <span className="w-2 h-2 rounded-full bg-cyber-muted" />
            <span>STREAM PAUSED</span>
          </div>
        )}

        {/* Stream Play/Stop Action */}
        <button
          onClick={onToggleStream}
          className={`px-3 py-1.5 rounded font-mono text-xs font-semibold flex items-center space-x-1.5 transition-all border ${
            isStreaming
              ? 'bg-cyber-red/20 border-cyber-red/50 text-cyber-red hover:bg-cyber-red/30'
              : 'bg-cyber-cyan/20 border-cyber-cyan/50 text-cyber-cyan hover:bg-cyber-cyan/30 shadow-cyan-glow'
          }`}
        >
          {isStreaming ? (
            <>
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>PAUSE</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>START STREAM</span>
            </>
          )}
        </button>

        {/* Global Security Posture */}
        <div className="hidden lg:flex items-center space-x-2 border-l border-cyber-border pl-4 font-mono text-xs text-cyber-muted">
          <ShieldCheck className="w-4 h-4 text-cyber-green" />
          <span>STATUS:</span>
          <strong className="text-cyber-green">SECURE</strong>
        </div>

        {/* Real-time UTC & Local Clock */}
        <div className="hidden md:flex items-center space-x-2 border-l border-cyber-border pl-4 font-mono text-xs">
          <Clock className="w-3.5 h-3.5 text-cyber-cyan" />
          <span className="text-cyber-text font-bold">{timeLocal}</span>
          <span className="text-cyber-muted text-[10px]">({timeUtc})</span>
        </div>

        {/* Notification Bell Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded bg-cyber-card border border-cyber-border text-cyber-muted hover:text-white relative transition-colors"
          >
            <Bell className="w-4 h-4" />
            {recentAlerts.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-cyber-red text-white text-[9px] font-bold rounded-full w-4 h-4 flex items-center justify-center font-mono">
                {recentAlerts.length > 9 ? '9+' : recentAlerts.length}
              </span>
            )}
          </button>

          {/* Notifications Flyout */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-cyber-card border border-cyber-border rounded-sm shadow-2xl z-50 p-2 font-mono text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-cyber-border px-2">
                <span className="font-bold text-white uppercase text-[11px]">Active Threat Alerts</span>
                <span className="text-[10px] text-cyber-red font-bold">{criticalCount} Critical</span>
              </div>
              <div className="max-h-64 overflow-y-auto space-y-1.5 pt-2">
                {recentAlerts.length > 0 ? (
                  recentAlerts.slice(0, 5).map((a, i) => (
                    <div
                      key={i}
                      onClick={() => {
                        onOpenAlert(a);
                        setShowNotifications(false);
                      }}
                      className="p-2 bg-cyber-surface hover:bg-cyber-surface/80 rounded border-l-2 border-cyber-red cursor-pointer transition-colors"
                    >
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="font-bold text-white">{a.threat_type}</span>
                        <span className="text-cyber-muted">{a.timestamp.slice(11, 19)}</span>
                      </div>
                      <p className="text-[11px] text-cyber-cyan mt-0.5 truncate">{a.source_ip}</p>
                    </div>
                  ))
                ) : (
                  <p className="p-3 text-center text-cyber-muted italic text-[11px]">
                    No threats currently active.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
