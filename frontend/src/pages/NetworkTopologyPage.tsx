import React, { useEffect, useState } from 'react';
import { Share2, Server, Shield, Globe, RefreshCw, Cpu, Activity } from 'lucide-react';
import { api } from '../services/api';
import { TopologyNode, TopologyEdge } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';

interface NetworkTopologyPageProps {
  onInvestigateIP: (ip: string) => void;
}

export const NetworkTopologyPage: React.FC<NetworkTopologyPageProps> = ({ onInvestigateIP }) => {
  const [nodes, setNodes] = useState<TopologyNode[]>([]);
  const [edges, setEdges] = useState<TopologyEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);
  const [loading, setLoading] = useState(false);

  const loadTopology = () => {
    setLoading(true);
    api.getNetworkTopology()
      .then((res) => {
        setNodes(res.nodes);
        setEdges(res.edges);
        if (res.nodes.length > 0 && !selectedNode) {
          setSelectedNode(res.nodes[0]);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTopology();
    const interval = setInterval(loadTopology, 5000);
    return () => clearInterval(interval);
  }, []);

  const getNodeColor = (node: TopologyNode) => {
    if (node.status === 'critical') return '#FF4D67';
    if (node.status === 'high') return '#FFBF69';
    if (node.status === 'filtering') return '#5B8CFF';
    if (node.status === 'targeted') return '#FF4D67';
    return '#39D5FF';
  };

  const getEdgeStroke = (edge: TopologyEdge) => {
    if (edge.status === 'critical') return '#FF4D67';
    if (edge.status === 'high') return '#FFBF69';
    return '#39D5FF';
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wider flex items-center space-x-2">
            <Share2 className="w-5 h-5 text-cyber-cyan" />
            <span>NETWORK TOPOLOGY &bull; ATTACK PATH VISUALIZATION</span>
          </h2>
          <p className="text-xs text-cyber-muted mt-0.5">
            Active flow graph linking external source IPs, the edge firewall, and internal target servers.
          </p>
        </div>
        <button
          onClick={loadTopology}
          disabled={loading}
          className="px-3 py-1.5 bg-cyber-card border border-cyber-border text-white text-xs hover:border-cyber-cyan rounded flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyber-cyan' : ''}`} />
          <span>Refresh Graph</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        {/* Interactive SVG Network Graph (3 Columns) */}
        <div className="lg:col-span-3 hud-card p-4 rounded-sm flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-cyber-border pb-2 mb-2">
            <span className="text-xs font-bold text-white uppercase flex items-center">
              <Activity className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              TOPOLOGY GRAPH CANVAS
            </span>
            <div className="flex items-center space-x-3 text-[11px]">
              <span className="flex items-center text-cyber-cyan">
                <span className="w-2.5 h-2.5 rounded-full bg-cyber-cyan mr-1.5" />
                Normal Client Path
              </span>
              <span className="flex items-center text-cyber-red">
                <span className="w-2.5 h-2.5 rounded-full bg-cyber-red mr-1.5 animate-pulse" />
                Active Attack Vector
              </span>
            </div>
          </div>

          <div className="w-full h-[450px] relative bg-cyber-bg/90 rounded border border-cyber-border/50 overflow-hidden flex items-center justify-center">
            {/* SVG Link Layer */}
            <svg className="w-full h-full absolute inset-0 pointer-events-none" viewBox="0 0 700 450">
              <defs>
                <linearGradient id="edgeGradCyan" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#39D5FF" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#39D5FF" stopOpacity="0.8" />
                </linearGradient>
                <linearGradient id="edgeGradRed" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#FF4D67" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#FF4D67" stopOpacity="1" />
                </linearGradient>
              </defs>

              {/* Render dynamic edges */}
              {edges.map((edge, idx) => {
                const srcNode = nodes.find((n) => n.id === edge.from);
                const dstNode = nodes.find((n) => n.id === edge.to);
                if (!srcNode || !dstNode) return null;

                const isCrit = edge.status === 'critical';
                const strokeColor = getEdgeStroke(edge);

                return (
                  <g key={idx}>
                    <line
                      x1={srcNode.x}
                      y1={srcNode.y}
                      x2={dstNode.x}
                      y2={dstNode.y}
                      stroke={strokeColor}
                      strokeWidth={isCrit ? 2.5 : 1.5}
                      strokeOpacity={isCrit ? 0.9 : 0.5}
                      strokeDasharray={isCrit ? '4,4' : undefined}
                    />
                    {/* Animated packet circles traveling along line */}
                    {isCrit && (
                      <circle r="3" fill="#FF4D67">
                        <animateMotion
                          path={`M ${srcNode.x} ${srcNode.y} L ${dstNode.x} ${dstNode.y}`}
                          dur="1.2s"
                          repeatCount="indefinite"
                        />
                      </circle>
                    )}
                  </g>
                );
              })}
            </svg>

            {/* Interactive Nodes */}
            {nodes.map((node) => {
              const color = getNodeColor(node);
              const isSelected = selectedNode?.id === node.id;

              return (
                <div
                  key={node.id}
                  onClick={() => {
                    setSelectedNode(node);
                    if (node.ip) onInvestigateIP(node.ip);
                  }}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-transform hover:scale-110 flex flex-col items-center group z-10`}
                  style={{ left: `${(node.x / 700) * 100}%`, top: `${(node.y / 450) * 100}%` }}
                >
                  <div
                    className={`w-9 h-9 rounded flex items-center justify-center border shadow-lg ${
                      isSelected ? 'ring-2 ring-white' : ''
                    }`}
                    style={{
                      backgroundColor: '#101A2B',
                      borderColor: color,
                      boxShadow: `0 0 15px ${color}40`,
                    }}
                  >
                    {node.type === 'client' && <Globe className="w-4 h-4" style={{ color }} />}
                    {node.type === 'gateway' && <Shield className="w-5 h-5" style={{ color }} />}
                    {node.type === 'server' && <Server className="w-4 h-4" style={{ color }} />}
                  </div>

                  <span className="text-[10px] font-bold text-white mt-1 bg-cyber-bg/90 px-1.5 py-0.5 rounded border border-cyber-border whitespace-nowrap">
                    {node.label}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="mt-3 pt-2 border-t border-cyber-border text-xs text-cyber-muted flex justify-between">
            <span>NETWORK SEGMENTS: <strong>Edge DMZ &bull; Internal Subnet 10.0.0.0/24</strong></span>
            <span>NODES VISIBLE: <strong>{nodes.length} Active</strong></span>
          </div>
        </div>

        {/* Node Inspector Panel (1 Column) */}
        <div className="hud-card p-4 rounded-sm flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-cyber-border pb-2 mb-3 flex items-center">
              <Cpu className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              NODE INSPECTOR
            </h3>

            {selectedNode ? (
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-cyber-muted text-[10px] block">NODE IDENTIFIER</span>
                  <strong className="text-white text-sm">{selectedNode.label}</strong>
                </div>

                <div>
                  <span className="text-cyber-muted text-[10px] block">NODE ROLE</span>
                  <span className="text-cyber-cyan uppercase font-bold">{selectedNode.type}</span>
                </div>

                <div>
                  <span className="text-cyber-muted text-[10px] block">SECURITY CLASSIFICATION</span>
                  <div className="mt-1">
                    <SeverityBadge severity={selectedNode.severity || 'LOW'} size="sm" />
                  </div>
                </div>

                {selectedNode.ip && (
                  <div>
                    <span className="text-cyber-muted text-[10px] block">IP ADDRESS</span>
                    <strong className="text-cyber-cyan font-bold">{selectedNode.ip}</strong>
                  </div>
                )}

                <div className="p-3 bg-cyber-surface rounded border border-cyber-border/70 text-xs">
                  <span className="text-[10px] text-cyber-muted uppercase block mb-1">Status Description</span>
                  <p className="text-cyber-text/90">
                    {selectedNode.status === 'critical'
                      ? 'Actively executing high-volume packet flood targeting 10.0.0.5.'
                      : selectedNode.status === 'targeted'
                      ? 'Targeted by high-density external incoming traffic.'
                      : 'Operating within expected baseline thresholds.'}
                  </p>
                </div>

                {selectedNode.ip && (
                  <button
                    onClick={() => onInvestigateIP(selectedNode.ip!)}
                    className="w-full py-2 bg-cyber-card border border-cyber-cyan/50 text-cyber-cyan hover:bg-cyber-cyan hover:text-black rounded font-bold text-xs transition-colors"
                  >
                    Open Full Host Forensics &rarr;
                  </button>
                )}
              </div>
            ) : (
              <p className="text-xs text-cyber-muted italic">Select any node on the graph to inspect metadata.</p>
            )}
          </div>

          <div className="pt-3 border-t border-cyber-border text-[11px] text-cyber-muted">
            Click nodes to trigger instant host investigation.
          </div>
        </div>
      </div>
    </div>
  );
};
