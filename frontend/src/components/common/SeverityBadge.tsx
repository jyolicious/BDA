import React from 'react';
import { ThreatSeverity } from '../../types';

interface SeverityBadgeProps {
  severity: ThreatSeverity | string;
  size?: 'sm' | 'md' | 'lg';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const sev = (severity || 'LOW').toUpperCase();

  const styles: Record<string, { bg: string; text: string; border: string; glow: string }> = {
    CRITICAL: {
      bg: 'bg-cyber-red/15',
      text: 'text-cyber-red',
      border: 'border-cyber-red/50',
      glow: 'shadow-[0_0_10px_rgba(255,77,103,0.3)]',
    },
    HIGH: {
      bg: 'bg-cyber-amber/15',
      text: 'text-cyber-amber',
      border: 'border-cyber-amber/50',
      glow: 'shadow-[0_0_10px_rgba(255,191,105,0.2)]',
    },
    MEDIUM: {
      bg: 'bg-cyber-blue/15',
      text: 'text-cyber-blue',
      border: 'border-cyber-blue/50',
      glow: '',
    },
    LOW: {
      bg: 'bg-cyber-green/15',
      text: 'text-cyber-green',
      border: 'border-cyber-green/50',
      glow: '',
    },
  };

  const current = styles[sev] || styles.LOW;
  const sizeClasses = {
    sm: 'text-[10px] px-1.5 py-0.5 tracking-wider',
    md: 'text-xs px-2.5 py-1 tracking-wider',
    lg: 'text-sm px-3 py-1.5 font-bold',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-mono font-semibold rounded border uppercase ${current.bg} ${current.text} ${current.border} ${current.glow} ${sizeClasses}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current animate-pulse" />
      {sev}
    </span>
  );
};
