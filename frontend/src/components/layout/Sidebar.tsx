import React, { useState } from 'react';
import {
  LayoutDashboard,
  Radio,
  Flame,
  Target,
  Share2,
  Layers,
  BarChart3,
  Cpu,
  FileText,
  Sliders,
  ChevronLeft,
  ChevronRight,
  Shield,
  Database,
  Server
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  isConnected: boolean;
  isStreaming: boolean;
  mongoConnected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  isConnected,
  isStreaming,
  mongoConnected,
}) => {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'monitor', label: 'Live Threat Monitor', icon: Radio },
    { id: 'simulator', label: 'Attack Simulator', icon: Flame, badge: 'DEMO' },
    { id: 'threat-intel', label: 'Threat Intelligence', icon: Target },
    { id: 'topology', label: 'Network Topology', icon: Share2 },
    { id: 'pipeline', label: 'Big Data Pipeline', icon: Layers },
    { id: 'analytics', label: 'Network Analytics', icon: BarChart3 },
    { id: 'architecture', label: 'System Architecture', icon: Cpu },
    { id: 'reports', label: 'Historical Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Sliders },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 h-screen z-40 bg-cyber-surface border-r border-cyber-border flex flex-col transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center px-4 border-b border-cyber-border justify-between">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-cyber-cyan to-cyber-blue flex items-center justify-center text-black font-extrabold shadow-cyan-glow flex-shrink-0">
            <Shield className="w-5 h-5 fill-black stroke-black" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-mono font-black text-base tracking-widest text-white leading-none">
                SENTINEL
              </span>
              <span className="font-mono text-[9px] text-cyber-cyan tracking-wider uppercase mt-0.5">
                CYBER THREAT SOC
              </span>
            </div>
          )}
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded text-cyber-muted hover:text-cyber-cyan hover:bg-cyber-card transition-colors flex-shrink-0"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center px-3 py-2.5 rounded text-xs font-mono tracking-wider transition-all relative group ${
                isActive
                  ? 'bg-cyber-card text-cyber-cyan font-bold border border-cyber-border shadow-sm'
                  : 'text-cyber-muted hover:text-cyber-text hover:bg-cyber-card/50'
              }`}
              title={collapsed ? item.label : undefined}
            >
              {/* Cyan indicator line on active */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-cyber-cyan rounded-r shadow-cyan-glow" />
              )}
              <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-cyber-cyan' : 'text-cyber-muted group-hover:text-cyber-text'}`} />
              {!collapsed && (
                <span className="ml-3 truncate flex-1 text-left">{item.label}</span>
              )}
              {!collapsed && item.badge && (
                <span className="text-[9px] bg-cyber-red/20 text-cyber-red border border-cyber-red/40 px-1.5 py-0.2 rounded font-bold">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Infrastructure Status Footer */}
      <div className="p-3 border-t border-cyber-border bg-cyber-bg/50 font-mono text-[10px] space-y-2">
        {!collapsed ? (
          <>
            <div className="flex items-center justify-between">
              <span className="text-cyber-muted flex items-center">
                <Server className="w-3 h-3 mr-1.5" /> API / WEBSOCKET
              </span>
              <span className={`font-bold flex items-center ${isConnected ? 'text-cyber-green' : 'text-cyber-red'}`}>
                <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${isConnected ? 'bg-cyber-green animate-pulse' : 'bg-cyber-red'}`} />
                {isConnected ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-cyber-muted flex items-center">
                <Database className="w-3 h-3 mr-1.5" /> MONGODB
              </span>
              <span className={`font-bold flex items-center ${mongoConnected ? 'text-cyber-green' : 'text-cyber-amber'}`}>
                <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${mongoConnected ? 'bg-cyber-green' : 'bg-cyber-amber'}`} />
                {mongoConnected ? 'CONNECTED' : 'STANDBY'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-cyber-muted flex items-center">
                <Radio className="w-3 h-3 mr-1.5" /> STREAM ENGINE
              </span>
              <span className={`font-bold ${isStreaming ? 'text-cyber-cyan' : 'text-cyber-muted'}`}>
                {isStreaming ? 'STREAMING' : 'PAUSED'}
              </span>
            </div>

            <div className="pt-1.5 border-t border-cyber-border/60 flex items-center justify-between text-cyber-muted/80">
              <span>ENV:</span>
              <span className="text-cyber-cyan font-bold">LOCAL LAB</span>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center space-y-2 py-1">
            <span
              className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-cyber-green animate-pulse' : 'bg-cyber-red'}`}
              title="API Connection"
            />
            <span
              className={`w-2.5 h-2.5 rounded-full ${mongoConnected ? 'bg-cyber-green' : 'bg-cyber-amber'}`}
              title="MongoDB Status"
            />
          </div>
        )}
      </div>
    </aside>
  );
};
