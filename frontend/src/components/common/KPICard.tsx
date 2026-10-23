import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'cyan' | 'red' | 'amber' | 'green' | 'blue';
  trend?: string;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'cyan',
  trend,
}) => {
  const variantStyles = {
    cyan: {
      border: 'hud-card',
      iconBg: 'bg-cyber-cyan/10 text-cyber-cyan border-cyber-cyan/30',
      valueColor: 'text-cyber-cyan',
      glow: 'hover:border-cyber-cyan/50',
    },
    red: {
      border: 'hud-card hud-card-red',
      iconBg: 'bg-cyber-red/10 text-cyber-red border-cyber-red/30',
      valueColor: 'text-cyber-red',
      glow: 'hover:border-cyber-red/50',
    },
    amber: {
      border: 'hud-card hud-card-amber',
      iconBg: 'bg-cyber-amber/10 text-cyber-amber border-cyber-amber/30',
      valueColor: 'text-cyber-amber',
      glow: 'hover:border-cyber-amber/50',
    },
    green: {
      border: 'hud-card',
      iconBg: 'bg-cyber-green/10 text-cyber-green border-cyber-green/30',
      valueColor: 'text-cyber-green',
      glow: 'hover:border-cyber-green/50',
    },
    blue: {
      border: 'hud-card',
      iconBg: 'bg-cyber-blue/10 text-cyber-blue border-cyber-blue/30',
      valueColor: 'text-cyber-blue',
      glow: 'hover:border-cyber-blue/50',
    },
  }[variant];

  return (
    <div
      className={`p-4 rounded-sm transition-all duration-200 ${variantStyles.border} ${variantStyles.glow}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-mono uppercase tracking-wider text-cyber-muted font-semibold">
          {title}
        </span>
        <div className={`p-1.5 rounded border ${variantStyles.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="flex items-baseline space-x-2">
        <span className={`text-2xl font-mono font-bold tracking-tight ${variantStyles.valueColor}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {trend && (
          <span className="text-[11px] font-mono text-cyber-cyan bg-cyber-cyan/10 px-1 rounded">
            {trend}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="text-[11px] text-cyber-muted/80 mt-1 font-mono truncate">
          {subtitle}
        </p>
      )}
    </div>
  );
};
