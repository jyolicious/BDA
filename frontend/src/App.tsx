import React, { useState } from 'react';
import { useTelemetry } from './hooks/useTelemetry';
import { Sidebar } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { InvestigationModal } from './components/common/InvestigationModal';

// Pages
import { Overview } from './pages/Overview';
import { LiveThreatMonitor } from './pages/LiveThreatMonitor';
import { AttackSimulator } from './pages/AttackSimulator';
import { ThreatInvestigation } from './pages/ThreatInvestigation';
import { NetworkTopologyPage } from './pages/NetworkTopologyPage';
import { BigDataPipelinePage } from './pages/BigDataPipelinePage';
import { NetworkAnalyticsPage } from './pages/NetworkAnalyticsPage';
import { SystemArchitecturePage } from './pages/SystemArchitecturePage';
import { HistoricalReportsPage } from './pages/HistoricalReportsPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [investigatingIP, setInvestigatingIP] = useState<string | null>(null);

  const {
    telemetry,
    isConnected,
    error,
    startStream,
    stopStream,
    setMode,
    triggerDemo,
  } = useTelemetry();

  const isStreaming = telemetry?.engine?.is_streaming || false;
  const activeMode = telemetry?.engine?.mode || 'NORMAL';
  const mongoConnected = telemetry?.services?.mongodb ?? true;
  const recentAlerts = telemetry?.recent_alerts || [];

  const tabTitles: Record<string, string> = {
    overview: 'Security Operations Center',
    monitor: 'Live Threat Monitor',
    simulator: 'Attack Simulator Control Room',
    'threat-intel': 'Threat Intelligence & Forensics',
    topology: 'Network Topology & Attack Paths',
    pipeline: 'Big Data Pipeline Orchestration',
    analytics: 'Network Analytics & MLlib Clusters',
    architecture: 'Lambda System Architecture',
    reports: 'Historical Benchmarks & Reports',
    settings: 'Detection Rules & Configuration',
  };

  return (
    <div className="min-h-screen bg-cyber-bg text-cyber-text font-sans flex overflow-x-hidden selection:bg-cyber-cyan selection:text-black">
      {/* Fixed Left Navigation Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        isConnected={isConnected}
        isStreaming={isStreaming}
        mongoConnected={mongoConnected}
      />

      {/* Main View Area */}
      <div className="flex-1 ml-16 md:ml-64 flex flex-col min-w-0 transition-all duration-300">
        {/* Sticky Top Navbar */}
        <Navbar
          pageTitle={tabTitles[currentTab] || 'Cyber Threat Intelligence'}
          isStreaming={isStreaming}
          onToggleStream={isStreaming ? stopStream : startStream}
          recentAlerts={recentAlerts}
          onOpenAlert={(alert) => setInvestigatingIP(alert.source_ip)}
          activeMode={activeMode}
        />

        {!telemetry && !error && (
          <div role="status" className="mx-6 mt-4 border border-cyber-border bg-cyber-card px-4 py-3 font-mono text-xs text-cyber-muted">
            Connecting to backend telemetry...
          </div>
        )}
        {error && (
          <div role="alert" className="mx-6 mt-4 border border-cyber-red/40 bg-cyber-red/10 px-4 py-3 font-mono text-xs text-cyber-red">
            {error}
          </div>
        )}

        {/* Page Content Body */}
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto animate-in fade-in duration-300">
          {currentTab === 'overview' && (
            <Overview
              telemetry={telemetry}
              onInvestigateIP={setInvestigatingIP}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'monitor' && (
            <LiveThreatMonitor
              telemetry={telemetry}
              onInvestigateIP={setInvestigatingIP}
            />
          )}

          {currentTab === 'simulator' && (
            <AttackSimulator
              telemetry={telemetry}
              onSetMode={setMode}
              onStartStream={startStream}
              onStopStream={stopStream}
              onTriggerDemo={triggerDemo}
              onInvestigateIP={setInvestigatingIP}
            />
          )}

          {currentTab === 'threat-intel' && (
            <ThreatInvestigation
              telemetry={telemetry}
              onInvestigateIP={setInvestigatingIP}
            />
          )}

          {currentTab === 'topology' && (
            <NetworkTopologyPage
              onInvestigateIP={setInvestigatingIP}
            />
          )}

          {currentTab === 'pipeline' && (
            <BigDataPipelinePage />
          )}

          {currentTab === 'analytics' && (
            <NetworkAnalyticsPage />
          )}

          {currentTab === 'architecture' && (
            <SystemArchitecturePage />
          )}

          {currentTab === 'reports' && (
            <HistoricalReportsPage />
          )}

          {currentTab === 'settings' && (
            <SettingsPage />
          )}
        </main>
      </div>

      {/* Host Forensics Investigation Modal */}
      {investigatingIP && (
        <InvestigationModal
          ip={investigatingIP}
          onClose={() => setInvestigatingIP(null)}
        />
      )}
    </div>
  );
}

export default App;
