import { ThreatAlert, SuspiciousIP, SparkClusterSummary, TopologyNode, TopologyEdge } from '../types';

const API_BASE = '/api';

export function getWebSocketUrl(): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}/ws/telemetry`;
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export const api = {
  // Health & System
  getHealth: () => request<any>('/health'),
  getTelemetry: () => request<any>('/telemetry'),

  // Alerts & Stream Data
  getAlerts: (limit = 50, minSeverity?: string) => {
    const query = minSeverity ? `?limit=${limit}&min_severity=${minSeverity}` : `?limit=${limit}`;
    return request<{ count: number; alerts: ThreatAlert[] }>(`/alerts${query}`);
  },
  getSuspiciousIPs: (limit = 15) => request<{ count: number; items: SuspiciousIP[] }>(`/suspicious-ips?limit=${limit}`),
  getThreatDistribution: () => request<{ distribution: Record<string, number> }>('/threat-distribution'),
  getTrafficHistory: () => request<{ history: any[] }>('/traffic-history'),
  getEvents: (limit = 30) => request<{ count: number; events: any[] }>(`/events?limit=${limit}`),

  // Host Deep Dive Investigation
  getInvestigation: (ip: string) => request<any>(`/investigation/${encodeURIComponent(ip)}`),

  // Simulation Controls
  startSimulation: () => request<any>('/simulation/start', { method: 'POST' }),
  stopSimulation: () => request<any>('/simulation/stop', { method: 'POST' }),
  setSimulationMode: (mode: string) => request<any>('/simulation/mode', {
    method: 'POST',
    body: JSON.stringify({ mode }),
  }),
  triggerDemo: (stepDuration = 4) => request<any>(`/simulation/demo?step_duration=${stepDuration}`, { method: 'POST' }),
  clearAlerts: () => request<any>('/alerts/clear', { method: 'POST' }),

  // Network Topology
  getNetworkTopology: () => request<{ nodes: TopologyNode[]; edges: TopologyEdge[]; timestamp: string }>('/network/topology'),

  // Big Data Pipeline & Analytics
  getBigDataStatus: () => request<any>('/bigdata/status'),
  getMapReduceAnalytics: () => request<{ executed: boolean; top_ips: any[]; attack_counts: any[] }>('/bigdata/mapreduce'),
  getSparkAnalytics: () => request<{ executed: boolean; cluster_summary: SparkClusterSummary[]; clusters_sample: any[] }>('/bigdata/spark'),
  getReports: () => request<{ available: boolean; benchmark_rows: any[]; markdown_report: string }>('/bigdata/reports'),

  // Job Run Triggers
  runDataGeneration: (events = 50000) => request<any>('/bigdata/run/generate', {
    method: 'POST',
    body: JSON.stringify({ events }),
  }),
  runHDFSUpload: () => request<any>('/bigdata/run/hdfs', { method: 'POST' }),
  runMapReduce: () => request<any>('/bigdata/run/mapreduce', { method: 'POST' }),
  runSpark: () => request<any>('/bigdata/run/spark', { method: 'POST' }),
  runSeedMongoDB: () => request<any>('/bigdata/run/seed', { method: 'POST' }),

  // Configuration
  getConfig: () => request<any>('/config'),
};
