export type ThreatSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AttackType = 'NORMAL' | 'DDOS' | 'PORT_SCAN' | 'ANOMALY' | 'HIGH_VOLUME' | 'OTHER';

export interface NetworkEvent {
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: 'TCP' | 'UDP' | 'ICMP';
  packet_count: number;
  bytes_sent: number;
  bytes_received: number;
  duration_ms: number;
  connection_status: 'SUCCESS' | 'FAILED' | 'TIMEOUT' | 'REJECTED';
  attack_label: string;
}

export interface ThreatAlert {
  timestamp: string;
  source_ip: string;
  destination_ip?: string;
  threat_type: string;
  threat_score: number;
  severity: ThreatSeverity;
  event_count: number;
  unique_ports: number;
  failed_connections: number;
  event_rate_per_sec?: number;
  byte_rate_per_sec?: number;
  detection_reason: string;
  score_breakdown?: any;
}

export interface SuspiciousIP {
  source_ip: string;
  threat_score: number;
  severity: ThreatSeverity;
  threat_types: string[] | string;
  alert_count?: number;
  event_count: number;
  last_seen: string;
}

export interface TrafficDataPoint {
  timestamp: string;
  rate: number;
  active_window: number;
  threats: number;
  mode: string;
}

export interface BloomFilterStats {
  capacity: number;
  target_error_rate: number;
  elements_added: number;
  num_bits: number;
  num_bytes: number;
  num_hash_functions: number;
  bits_set: number;
  fill_ratio: number;
  current_fpp: number;
  memory_usage_kb: number;
}

export interface SlidingWindowStats {
  active_events: number;
  active_ips: number;
  window_duration_seconds: number;
}

export interface EngineStatus {
  is_streaming: boolean;
  mode: string;
  target_rate_eps: number;
  uptime_seconds: number;
  events_processed: number;
  events_per_second: number;
  threats_detected: number;
  critical_alerts: number;
}

export interface DemoStatus {
  is_running: boolean;
  current_phase: string | null;
  progress_pct: number;
  message: string;
}

export interface TelemetryPayload {
  type: string;
  timestamp: string;
  engine: EngineStatus;
  sliding_window: SlidingWindowStats;
  bloom_filter: BloomFilterStats;
  traffic_history: TrafficDataPoint[];
  recent_events: NetworkEvent[];
  recent_alerts: ThreatAlert[];
  top_suspicious_ips: SuspiciousIP[];
  threat_distribution: Record<string, number>;
  demo_status: DemoStatus;
  services: {
    mongodb: boolean;
    hdfs_native: boolean;
  };
}

export interface SparkClusterSummary {
  cluster: string | number;
  host_count: number;
  mean_event_count?: number;
  mean_bytes_sent: number;
  mean_bytes_recv?: number;
  mean_packet_count?: number;
  mean_unique_ports: number;
  mean_failed_conns: number;
  assigned_profile: string;
  threat_severity: ThreatSeverity;
  detection_rationale: string;
}

export interface TopologyNode {
  id: string;
  label: string;
  ip?: string;
  type: 'client' | 'gateway' | 'server';
  status: 'normal' | 'high' | 'critical' | 'filtering' | 'targeted';
  severity?: ThreatSeverity;
  x: number;
  y: number;
}

export interface TopologyEdge {
  from: string;
  to: string;
  status: 'normal' | 'high' | 'critical';
}
