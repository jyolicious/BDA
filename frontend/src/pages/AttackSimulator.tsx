import React, { useState } from 'react';
import {
  Flame,
  Shield,
  Search,
  Activity,
  Play,
  Square,
  CheckCircle2,
  Radio,
  Sparkles,
  Cpu,
  Layers,
} from 'lucide-react';
import { TelemetryPayload } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';

interface AttackSimulatorProps {
  telemetry: TelemetryPayload | null;
  onSetMode: (mode: string) => void;
  onStartStream: () => void;
  onStopStream: () => void;
  onTriggerDemo: (duration?: number) => void;
  onInvestigateIP: (ip: string) => void;
}

export const AttackSimulator: React.FC<AttackSimulatorProps> = ({
  telemetry,
  onSetMode,
  onStartStream,
  onStopStream,
  onTriggerDemo,
  onInvestigateIP,
}) => {
  const [stepDuration, setStepDuration] = useState(4);

  const engine = telemetry?.engine || {
    is_streaming: false,
    mode: 'NORMAL',
    events_processed: 0,
    events_per_second: 0,
    threats_detected: 0,
    critical_alerts: 0,
    uptime_seconds: 0,
    target_rate_eps: 40,
  };

  const demoStatus = telemetry?.demo_status || {
    is_running: false,
    current_phase: null,
    progress_pct: 0,
    message: 'Standby',
  };

  const recentAlerts = telemetry?.recent_alerts || [];
  const latestAlert = recentAlerts[0] || null;

  const attackCards = [
    {
      id: 'NORMAL',
      title: 'A. NORMAL TRAFFIC',
      subtitle: 'Baseline Workload Profile',
      description: 'Generates standard enterprise HTTP/HTTPS and DNS flows. Flow volume, duration, and ports conform to safe operating parameters.',
      rate: '40 ev/s',
      expectedSeverity: 'LOW',
      icon: Shield,
      accentColor: 'border-cyber-green/40 hover:border-cyber-green text-cyber-green',
      glow: 'shadow-[0_0_15px_rgba(53,230,161,0.15)]',
      bgGlow: 'bg-cyber-green/5',
      activeRing: 'ring-2 ring-cyber-green',
    },
    {
      id: 'DDOS',
      title: 'B. SIMULATE DDOS FLOOD',
      subtitle: 'Volumetric SYN / UDP Burst',
      description: 'Fires high-frequency burst (250+ ev/s) with extreme packet rates targeting ports 80/443. Triggers sliding-window rate threshold.',
      rate: '250 ev/s',
      expectedSeverity: 'CRITICAL',
      icon: Flame,
      accentColor: 'border-cyber-red/50 hover:border-cyber-red text-cyber-red',
      glow: 'shadow-[0_0_20px_rgba(255,77,103,0.3)]',
      bgGlow: 'bg-cyber-red/5',
      activeRing: 'ring-2 ring-cyber-red',
    },
    {
      id: 'PORT_SCAN',
      title: 'C. SIMULATE PORT SCAN',
      subtitle: 'Horizontal Reconnaissance Sweep',
      description: 'Probes across hundreds of destination ports in rapid succession with high connection drop ratios (SYN -> RST/Timeout).',
      rate: '120 ev/s',
      expectedSeverity: 'HIGH',
      icon: Search,
      accentColor: 'border-cyber-amber/50 hover:border-cyber-amber text-cyber-amber',
      glow: 'shadow-[0_0_20px_rgba(255,191,105,0.2)]',
      bgGlow: 'bg-cyber-amber/5',
      activeRing: 'ring-2 ring-cyber-amber',
    },
    {
      id: 'ANOMALY',
      title: 'D. SIMULATE ANOMALY',
      subtitle: 'Covert Data Exfiltration',
      description: 'Simulates severe data exfiltration asymmetry (sent >> received) on non-standard backdoor ports (4444, 1337, 31337).',
      rate: '60 ev/s',
      expectedSeverity: 'HIGH',
      icon: Activity,
      accentColor: 'border-cyber-cyan/50 hover:border-cyber-cyan text-cyber-cyan',
      glow: 'shadow-[0_0_20px_rgba(57,213,255,0.2)]',
      bgGlow: 'bg-cyber-cyan/5',
      activeRing: 'ring-2 ring-cyber-cyan',
    },
  ];

  // 8-stage timeline progress indicator
  const stages = [
    { num: 1, label: 'Simulation Activated', active: engine.is_streaming, done: engine.is_streaming },
    { num: 2, label: 'Synthetic Telemetry Generated', active: engine.is_streaming, done: engine.events_processed > 0 },
    { num: 3, label: 'Stream Ingestion Engine', active: engine.is_streaming, done: engine.events_processed > 10 },
    { num: 4, label: '5-Min Sliding Window Updated', active: engine.is_streaming, done: engine.events_processed > 20 },
    { num: 5, label: 'Bloom Filter & Heuristics Check', active: engine.is_streaming, done: engine.events_processed > 30 },
    { num: 6, label: 'Multi-Factor Threat Score Computed', active: engine.mode !== 'NORMAL', done: engine.threats_detected > 0 },
    { num: 7, label: 'Threat Alert Persisted to MongoDB', active: engine.threats_detected > 0, done: engine.threats_detected > 0 },
    { num: 8, label: 'Real-Time SOC Dashboard Live Update', active: true, done: true },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-4 bg-cyber-surface border border-cyber-border rounded-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="p-1 rounded bg-cyber-red/20 text-cyber-red border border-cyber-red/40">
              <Flame className="w-4 h-4 fill-current" />
            </span>
            <h2 className="text-lg font-mono font-bold text-white tracking-wider">
              CONTROL ROOM &bull; CONTROLLED ATTACK SIMULATION
            </h2>
          </div>
          <p className="text-xs font-mono text-cyber-muted mt-1 max-w-2xl">
            Controlled synthetic telemetry simulator. Generates live attack traffic patterns to prove real-time detection, sliding window evaluation, and alert persistence in live academic demonstrations.
          </p>
        </div>

        {/* Global Demo Scenario Trigger */}
        <div className="flex items-center space-x-3 bg-cyber-card p-2 rounded border border-cyber-border">
          <div className="text-right">
            <span className="text-[10px] font-mono text-cyber-muted block uppercase">Phase Duration</span>
            <select
              value={stepDuration}
              onChange={(e) => setStepDuration(Number(e.target.value))}
              disabled={demoStatus.is_running}
              className="bg-cyber-surface text-xs font-mono font-bold text-cyber-cyan border border-cyber-border rounded px-2 py-0.5 outline-none cursor-pointer"
            >
              <option value={2}>2s (Fast)</option>
              <option value={4}>4s (Standard)</option>
              <option value={8}>8s (Deep)</option>
            </select>
          </div>
          <button
            onClick={() => onTriggerDemo(stepDuration)}
            disabled={demoStatus.is_running}
            className={`px-4 py-2 rounded font-mono text-xs font-bold transition-all flex items-center space-x-2 ${
              demoStatus.is_running
                ? 'bg-cyber-muted/20 text-cyber-muted border border-cyber-muted/30 cursor-not-allowed'
                : 'bg-gradient-to-r from-cyber-cyan to-cyber-blue text-black font-extrabold hover:shadow-cyan-glow'
            }`}
          >
            <Sparkles className="w-4 h-4 fill-current" />
            <span>{demoStatus.is_running ? 'DEMO RUNNING...' : 'RUN ACADEMIC DEMO'}</span>
          </button>
        </div>
      </div>

      {/* Demo Scenario Progress Banner (Visible when Demo is active) */}
      {demoStatus.is_running && (
        <div className="p-4 bg-cyber-card border-2 border-cyber-cyan rounded-sm shadow-cyan-glow animate-pulse-subtle font-mono">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Radio className="w-4 h-4 text-cyber-cyan animate-pulse" />
              <span className="text-xs font-bold text-white uppercase">
                {demoStatus.current_phase || 'DEMO SCENARIO IN PROGRESS'}
              </span>
            </div>
            <span className="text-xs text-cyber-cyan font-bold">{demoStatus.progress_pct}%</span>
          </div>
          <div className="w-full bg-cyber-bg h-2 rounded overflow-hidden">
            <div
              className="bg-cyber-cyan h-full transition-all duration-500"
              style={{ width: `${demoStatus.progress_pct}%` }}
            />
          </div>
          <p className="text-xs text-cyber-muted mt-2">
            Status: <strong className="text-white">{demoStatus.message}</strong>
          </p>
        </div>
      )}

      {/* 4 Large Simulation Control Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {attackCards.map((card) => {
          const Icon = card.icon;
          const isSelected = engine.mode === card.id;

          return (
            <div
              key={card.id}
              className={`p-4 rounded-sm border bg-cyber-card transition-all duration-200 flex flex-col justify-between ${card.accentColor} ${
                isSelected ? `${card.activeRing} ${card.glow} ${card.bgGlow}` : 'border-cyber-border'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="p-2 rounded bg-cyber-bg border border-current">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded border border-current font-bold uppercase">
                    {card.rate}
                  </span>
                </div>

                <h3 className="text-sm font-mono font-bold tracking-wider text-white">
                  {card.title}
                </h3>
                <span className="text-[11px] font-mono text-cyber-muted block mb-2 font-medium">
                  {card.subtitle}
                </span>

                <p className="text-xs text-cyber-muted/90 font-mono leading-relaxed mb-4">
                  {card.description}
                </p>
              </div>

              <div>
                <div className="flex items-center justify-between text-[11px] font-mono border-t border-cyber-border/60 pt-2 mb-3">
                  <span className="text-cyber-muted">EXPECTED THREAT:</span>
                  <SeverityBadge severity={card.expectedSeverity} size="sm" />
                </div>

                <button
                  onClick={() => onSetMode(card.id)}
                  className={`w-full py-2 px-3 rounded font-mono text-xs font-bold transition-all uppercase flex items-center justify-center space-x-2 ${
                    isSelected
                      ? 'bg-current text-black font-extrabold shadow-md'
                      : 'bg-cyber-bg hover:bg-cyber-surface border border-current text-current'
                  }`}
                >
                  {isSelected ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>CURRENTLY ACTIVE</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>ACTIVATE PROFILE</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real-Time Simulation Status & Stage Progression Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: Simulation Telemetry Status Panel (1 Column) */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between font-mono">
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-cyber-border pb-2 mb-3 flex items-center">
              <Cpu className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              SIMULATION ENGINE TELEMETRY
            </h3>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between p-2 rounded bg-cyber-surface border border-cyber-border/60">
                <span className="text-cyber-muted">ACTIVE MODE:</span>
                <strong className={engine.mode === 'DDOS' ? 'text-cyber-red' : (engine.mode === 'PORT_SCAN' ? 'text-cyber-amber' : 'text-cyber-cyan')}>
                  {engine.mode}
                </strong>
              </div>

              <div className="flex justify-between p-2 rounded bg-cyber-surface border border-cyber-border/60">
                <span className="text-cyber-muted">STREAM VELOCITY:</span>
                <strong className="text-white">{engine.events_per_second.toFixed(1)} ev/s</strong>
              </div>

              <div className="flex justify-between p-2 rounded bg-cyber-surface border border-cyber-border/60">
                <span className="text-cyber-muted">TOTAL FLOWS PRODUCED:</span>
                <strong className="text-white">{engine.events_processed.toLocaleString()}</strong>
              </div>

              <div className="flex justify-between p-2 rounded bg-cyber-surface border border-cyber-border/60">
                <span className="text-cyber-muted">SIMULATION UPTIME:</span>
                <strong className="text-white">{Math.floor(engine.uptime_seconds)} seconds</strong>
              </div>

              <div className="flex justify-between p-2 rounded bg-cyber-surface border border-cyber-border/60">
                <span className="text-cyber-muted">THREAT ALERTS PRODUCED:</span>
                <strong className="text-cyber-red">{engine.threats_detected} alerts</strong>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-cyber-border flex space-x-2">
            <button
              onClick={engine.is_streaming ? onStopStream : onStartStream}
              className={`flex-1 py-2 rounded text-xs font-bold flex items-center justify-center space-x-1.5 border transition-all ${
                engine.is_streaming
                  ? 'bg-cyber-red/20 border-cyber-red/50 text-cyber-red hover:bg-cyber-red/30'
                  : 'bg-cyber-cyan/20 border-cyber-cyan/50 text-cyber-cyan hover:bg-cyber-cyan/30'
              }`}
            >
              {engine.is_streaming ? <Square className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              <span>{engine.is_streaming ? 'HALT STREAM' : 'RESUME STREAM'}</span>
            </button>
          </div>
        </div>

        {/* Right: 8-Stage Attack Progression Pipeline (2 Columns) */}
        <div className="lg:col-span-2 hud-card p-4 rounded-sm font-mono flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cyber-border pb-2 mb-3">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                <Layers className="w-4 h-4 mr-1.5 text-cyber-cyan" />
                END-TO-END ATTACK PROGRESSION TIMELINE
              </h3>
              <span className="text-[10px] text-cyber-muted">VERIFIED BACKEND INSTRUMENTATION</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {stages.map((stage) => (
                <div
                  key={stage.num}
                  className={`p-2.5 rounded border flex items-center space-x-3 transition-colors ${
                    stage.done
                      ? 'bg-cyber-surface/90 border-cyber-green/40 text-white'
                      : stage.active
                      ? 'bg-cyber-card border-cyber-cyan/50 text-cyber-cyan'
                      : 'bg-cyber-bg/40 border-cyber-border/40 text-cyber-muted'
                  }`}
                >
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] flex-shrink-0 ${
                      stage.done
                        ? 'bg-cyber-green text-black'
                        : stage.active
                        ? 'bg-cyber-cyan text-black animate-pulse'
                        : 'bg-cyber-border text-cyber-muted'
                    }`}
                  >
                    {stage.num}
                  </div>
                  <div className="flex-1 truncate">
                    <span className="block font-semibold truncate">{stage.label}</span>
                    <span className="text-[10px] text-cyber-muted block">
                      {stage.done ? 'COMPLETED & VERIFIED' : (stage.active ? 'PROCESSING...' : 'STANDBY')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Active Resulting Threat Box */}
          {latestAlert && (
            <div className="mt-4 p-3 bg-cyber-bg border-l-4 border-cyber-red rounded text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-cyber-red">LATEST DETECTOR ACKNOWLEDGEMENT:</span>
                  <SeverityBadge severity={latestAlert.severity} size="sm" />
                  <span className="text-white font-bold">{latestAlert.threat_type}</span>
                </div>
                <p className="text-[11px] text-cyber-muted mt-0.5 truncate max-w-xl">
                  Host: <strong className="text-cyber-cyan">{latestAlert.source_ip}</strong> &bull; Reason: {latestAlert.detection_reason}
                </p>
              </div>
              <button
                onClick={() => onInvestigateIP(latestAlert.source_ip)}
                className="px-3 py-1 bg-cyber-card border border-cyber-border text-white text-[11px] hover:border-cyber-cyan rounded flex-shrink-0"
              >
                Inspect Threat &rarr;
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
