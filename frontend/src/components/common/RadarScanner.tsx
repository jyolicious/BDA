import React from 'react';
import { ThreatAlert } from '../../types';

interface RadarScannerProps {
  alerts?: ThreatAlert[];
  activeThreatCount?: number;
  size?: number;
}

export const RadarScanner: React.FC<RadarScannerProps> = ({
  alerts = [],
  activeThreatCount = 0,
  size = 280,
}) => {
  // Generate deterministic blips from alerts
  const blips = alerts.slice(0, 8).map((alert, idx) => {
    // Hash IP string to polar angle and radius
    const hash = alert.source_ip.split('.').reduce((acc, part) => acc + parseInt(part || '0', 10), 0) + idx * 45;
    const angle = (hash * 37) % 360;
    const radius = 25 + ((hash * 13) % 65); // 25% to 90% radius
    const rad = (angle * Math.PI) / 180;
    const x = 50 + (radius / 2) * Math.cos(rad);
    const y = 50 + (radius / 2) * Math.sin(rad);

    const isCritical = alert.severity === 'CRITICAL';
    const isHigh = alert.severity === 'HIGH';

    return {
      id: `${alert.source_ip}-${idx}`,
      ip: alert.source_ip,
      threat: alert.threat_type,
      severity: alert.severity,
      x,
      y,
      color: isCritical ? '#FF4D67' : (isHigh ? '#FFBF69' : '#39D5FF'),
    };
  });

  return (
    <div className="flex flex-col items-center justify-center p-3 relative">
      <div
        className="relative rounded-full border border-cyber-border/70 overflow-hidden bg-cyber-bg/80 flex items-center justify-center shadow-[inset_0_0_30px_rgba(57,213,255,0.05)]"
        style={{ width: size, height: size }}
      >
        {/* Concentric rings */}
        <div className="absolute w-[25%] h-[25%] rounded-full border border-cyber-border/50" />
        <div className="absolute w-[50%] h-[50%] rounded-full border border-cyber-border/60" />
        <div className="absolute w-[75%] h-[75%] rounded-full border border-cyber-border/50" />
        <div className="absolute w-full h-full rounded-full border border-cyber-cyan/30" />

        {/* Crosshair lines */}
        <div className="absolute w-full h-[1px] bg-cyber-border/60" />
        <div className="absolute h-full w-[1px] bg-cyber-border/60" />

        {/* Diagonal axis markers */}
        <div className="absolute w-full h-[1px] bg-cyber-border/25 rotate-45" />
        <div className="absolute w-full h-[1px] bg-cyber-border/25 -rotate-45" />

        {/* Angle Labels */}
        <span className="absolute top-1 text-[9px] font-mono text-cyber-muted/70">000°</span>
        <span className="absolute bottom-1 text-[9px] font-mono text-cyber-muted/70">180°</span>
        <span className="absolute left-1 text-[9px] font-mono text-cyber-muted/70">270°</span>
        <span className="absolute right-1 text-[9px] font-mono text-cyber-muted/70">090°</span>

        {/* Radar Sweeping Beam */}
        <div
          className="absolute w-full h-full rounded-full pointer-events-none animate-radar-sweep"
          style={{
            background: 'conic-gradient(from 0deg, rgba(57, 213, 255, 0.28) 0deg, rgba(57, 213, 255, 0.0) 65deg, transparent 65deg)',
          }}
        />

        {/* Threat Blips */}
        {blips.map((b) => (
          <div
            key={b.id}
            className="absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
            style={{ left: `${b.x}%`, top: `${b.y}%` }}
          >
            <div
              className="w-2.5 h-2.5 rounded-full animate-ping opacity-75 absolute"
              style={{ backgroundColor: b.color }}
            />
            <div
              className="w-2 h-2 rounded-full border border-black"
              style={{ backgroundColor: b.color }}
            />
            {/* Tooltip on hover */}
            <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-full mb-1 left-1/2 -translate-x-1/2 bg-cyber-card border border-cyber-border p-1 rounded text-[10px] font-mono whitespace-nowrap z-30 shadow-lg pointer-events-none">
              <span className="text-white font-bold">{b.ip}</span> | {b.threat} ({b.severity})
            </div>
          </div>
        ))}
      </div>

      {/* Radar Status Footer */}
      <div className="mt-3 flex items-center justify-between w-full text-[11px] font-mono border-t border-cyber-border/60 pt-2 text-cyber-muted">
        <span>ACTIVE BLIPS: <strong className="text-cyber-cyan">{blips.length}</strong></span>
        <span>SCAN RADIUS: <strong className="text-cyber-text">300s WINDOW</strong></span>
        <span className="text-cyber-green flex items-center">
          <span className="w-1.5 h-1.5 rounded-full bg-cyber-green inline-block mr-1 animate-pulse" />
          RADAR LOCK
        </span>
      </div>
    </div>
  );
};
