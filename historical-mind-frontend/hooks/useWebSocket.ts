'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { SimulationEvent } from '@/types/simulation';

export function useWebSocket(simulationId: string | null) {
  const [events, setEvents] = useState<SimulationEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!simulationId) return;

    // Connect to WebSocket
    const wsUrl = `ws://localhost:8000/ws/simulations/${simulationId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data: SimulationEvent = JSON.parse(event.data);
        setEvents((prev) => [...prev, data]);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [simulationId]);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  return { events, isConnected, clearEvents };
}
