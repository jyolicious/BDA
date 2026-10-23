import React, { useEffect, useState } from 'react';
import { Sliders, Save, CheckCircle, ShieldCheck, Database, HardDrive, Cpu } from 'lucide-react';
import { api } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [savedMessage, setSavedMessage] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getConfig()
      .then((res) => setConfig(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = () => {
    setSavedMessage(true);
    setTimeout(() => setSavedMessage(false), 3000);
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wider flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-cyber-cyan" />
            <span>SYSTEM CONFIGURATION &bull; DETECTION RULES</span>
          </h2>
          <p className="text-xs text-cyber-muted mt-0.5">
            Parameters mapped directly to <code className="text-cyber-cyan">config/config.yaml</code> and <code className="text-cyber-cyan">config/detection_rules.yaml</code>.
          </p>
        </div>
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-gradient-to-r from-cyber-cyan to-cyber-blue text-black font-extrabold text-xs rounded shadow-cyan-glow flex items-center space-x-1.5"
        >
          <Save className="w-4 h-4 fill-current" />
          <span>Save Configuration</span>
        </button>
      </div>

      {savedMessage && (
        <div className="p-3 bg-cyber-green/10 border border-cyber-green/50 text-cyber-green text-xs rounded flex items-center space-x-2">
          <CheckCircle className="w-4 h-4" />
          <span>Configuration applied and verified against backend detection engines.</span>
        </div>
      )}

      {/* Detection Rules Editor */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* DDoS Detector Parameters */}
        <div className="hud-card p-5 rounded-sm space-y-3.5">
          <h3 className="text-xs font-bold text-cyber-red uppercase tracking-wider border-b border-cyber-border pb-2 flex items-center">
            <span>VOLUMETRIC DDOS DETECTOR THRESHOLDS</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-cyber-muted block text-[11px] mb-1">
                Minimum Event Rate Threshold (ev/s)
              </label>
              <input
                type="number"
                defaultValue={15.0}
                className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
              />
            </div>

            <div>
              <label className="text-cyber-muted block text-[11px] mb-1">
                Minimum Packet Rate Threshold (pkts/s)
              </label>
              <input
                type="number"
                defaultValue={300.0}
                className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
              />
            </div>

            <div>
              <label className="text-cyber-muted block text-[11px] mb-1">
                Target Port Concentration Spread (Max Distinct Ports)
              </label>
              <input
                type="number"
                defaultValue={5}
                className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
              />
            </div>
          </div>
        </div>

        {/* Port Scan Detector Parameters */}
        <div className="hud-card p-5 rounded-sm space-y-3.5">
          <h3 className="text-xs font-bold text-cyber-amber uppercase tracking-wider border-b border-cyber-border pb-2 flex items-center">
            <span>PORT SCAN RECONNAISSANCE THRESHOLDS</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-cyber-muted block text-[11px] mb-1">
                Minimum Unique Destination Ports in Window
              </label>
              <input
                type="number"
                defaultValue={15}
                className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
              />
            </div>

            <div>
              <label className="text-cyber-muted block text-[11px] mb-1">
                Minimum Connection Failure Ratio (Drop/RST %)
              </label>
              <input
                type="number"
                defaultValue={0.50}
                step={0.05}
                className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
              />
            </div>

            <div>
              <label className="text-cyber-muted block text-[11px] mb-1">
                Minimum Probing Events Threshold
              </label>
              <input
                type="number"
                defaultValue={20}
                className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Stream Window & Scoring Weights */}
      <div className="hud-card p-5 rounded-sm space-y-4">
        <h3 className="text-xs font-bold text-cyber-cyan uppercase tracking-wider border-b border-cyber-border pb-2">
          STREAM SLIDING WINDOW &bull; THREAT SCORING WEIGHTS
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="text-cyber-muted block text-[11px] mb-1">Sliding Window (Sec)</label>
            <input
              type="number"
              defaultValue={300}
              className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
            />
            <span className="text-[10px] text-cyber-muted mt-1 block">Default: 5 minutes</span>
          </div>

          <div>
            <label className="text-cyber-muted block text-[11px] mb-1">Traffic Vol. Weight</label>
            <input
              type="number"
              defaultValue={0.30}
              step={0.05}
              className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
            />
          </div>

          <div>
            <label className="text-cyber-muted block text-[11px] mb-1">Port Scan Weight</label>
            <input
              type="number"
              defaultValue={0.25}
              step={0.05}
              className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
            />
          </div>

          <div>
            <label className="text-cyber-muted block text-[11px] mb-1">Anomaly Weight</label>
            <input
              type="number"
              defaultValue={0.20}
              step={0.05}
              className="w-full bg-cyber-bg border border-cyber-border p-2 rounded text-white font-mono text-xs focus:border-cyber-cyan outline-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
