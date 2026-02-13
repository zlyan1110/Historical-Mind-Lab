'use client';

import { useState, useCallback } from 'react';
import {
  CreateSimulationRequest,
  SimulationState,
  Decision,
} from '@/types/simulation';

const API_BASE_URL = 'http://localhost:8000';

export function useSimulation() {
  const [simulations, setSimulations] = useState<SimulationState[]>([]);
  const [currentSimulation, setCurrentSimulation] = useState<SimulationState | null>(null);
  const [history, setHistory] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createSimulation = useCallback(async (request: CreateSimulationRequest) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/simulations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Failed to create simulation: ${response.statusText}`);
      }

      const data: SimulationState = await response.json();
      setCurrentSimulation(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getSimulationState = useCallback(async (simulationId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}/state`);

      if (!response.ok) {
        throw new Error(`Failed to get simulation state: ${response.statusText}`);
      }

      const data: SimulationState = await response.json();
      setCurrentSimulation(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const startSimulation = useCallback(async (simulationId: string, maxTurns: number = 10) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_turns: maxTurns }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start simulation: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const stepSimulation = useCallback(async (simulationId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}/step`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Failed to step simulation: ${response.statusText}`);
      }

      const data: SimulationState = await response.json();
      setCurrentSimulation(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getHistory = useCallback(async (simulationId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}/history`);

      if (!response.ok) {
        throw new Error(`Failed to get history: ${response.statusText}`);
      }

      const data: Decision[] = await response.json();
      setHistory(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const listSimulations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/simulations`);

      if (!response.ok) {
        throw new Error(`Failed to list simulations: ${response.statusText}`);
      }

      const data: SimulationState[] = await response.json();
      setSimulations(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    simulations,
    currentSimulation,
    history,
    loading,
    error,
    createSimulation,
    getSimulationState,
    startSimulation,
    stepSimulation,
    getHistory,
    listSimulations,
  };
}
