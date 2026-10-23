import { useState, useEffect, useCallback, useRef } from 'react';
import { TelemetryPayload } from '../types';
import { api, getWebSocketUrl } from '../services/api';

export function useTelemetry() {
  const [telemetry, setTelemetry] = useState<TelemetryPayload | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const connectionGenerationRef = useRef(0);
  const connectRef = useRef<(generation: number) => void>(() => {});

  const connectWebSocket = useCallback((generation: number) => {
    try {
      const url = getWebSocketUrl();
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (connectionGenerationRef.current !== generation) return;
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        if (connectionGenerationRef.current !== generation) return;
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'TELEMETRY_UPDATE') {
            setTelemetry(data);
            setLastUpdated(new Date());
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message', err);
        }
      };

      ws.onerror = () => {
        if (connectionGenerationRef.current !== generation) return;
        setError('WebSocket connection error. Retrying telemetry connection.');
      };

      ws.onclose = () => {
        if (connectionGenerationRef.current !== generation) return;
        setIsConnected(false);
        // Attempt reconnection after 2.5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectRef.current(generation);
        }, 2500);
      };
    } catch (err: any) {
      if (connectionGenerationRef.current !== generation) return;
      setError(err?.message || 'WebSocket initialization failed');
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    connectRef.current = connectWebSocket;
  }, [connectWebSocket]);

  useEffect(() => {
    const generation = ++connectionGenerationRef.current;
    const connectionTimeout = window.setTimeout(() => connectWebSocket(generation), 0);
    return () => {
      connectionGenerationRef.current += 1;
      clearTimeout(connectionTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connectWebSocket]);

  // Actions
  const startStream = useCallback(async () => {
    try {
      await api.startSimulation();
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  const stopStream = useCallback(async () => {
    try {
      await api.stopSimulation();
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  const setMode = useCallback(async (mode: string) => {
    try {
      await api.setSimulationMode(mode);
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  const triggerDemo = useCallback(async (duration = 4) => {
    try {
      await api.triggerDemo(duration);
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  const clearAlerts = useCallback(async () => {
    try {
      await api.clearAlerts();
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  return {
    telemetry,
    isConnected,
    lastUpdated,
    error,
    startStream,
    stopStream,
    setMode,
    triggerDemo,
    clearAlerts,
  };
}
