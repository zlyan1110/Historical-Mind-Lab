'use client';

import { useState, useEffect, useMemo } from 'react';
import Map from '@/components/Map';
import { useSimulation } from '@/hooks/useSimulation';
import { useWebSocket } from '@/hooks/useWebSocket';
import { SimulationEvent } from '@/types/simulation';

export default function Home() {
  const [simulationId, setSimulationId] = useState<string | null>(null);
  const [agentName, setAgentName] = useState('颜之推 (Yan Zhitui)');
  const [startingLocation, setStartingLocation] = useState('建康');
  const [startingStress, setStartingStress] = useState(40);
  const [maxTurns, setMaxTurns] = useState(10);

  const {
    currentSimulation,
    history,
    loading,
    error,
    createSimulation,
    getSimulationState,
    startSimulation,
    stepSimulation,
    getHistory,
  } = useSimulation();

  const { events, isConnected, clearEvents } = useWebSocket(simulationId);

  // Update simulation state when WebSocket events indicate completion or state change
  useEffect(() => {
    if (!simulationId || events.length === 0) return;

    const latestEvent = events[events.length - 1];

    // When simulation completes or state updates, refresh the simulation state
    if (latestEvent.type === 'simulation_completed' || latestEvent.type === 'state_update') {
      getSimulationState(simulationId).catch(err => {
        console.error('Failed to refresh simulation state:', err);
      });
    }
  }, [events, simulationId, getSimulationState]);

  // Build location history from WebSocket events
  const locationHistory = useMemo(() => {
    const locations: any[] = [];
    const seenLocations = new Set<string>();

    console.log('Building location history from events:', events.length);

    // Extract location data from WebSocket events
    events.forEach((event, index) => {
      console.log(`Event ${index}:`, event.type, event.data?.location?.name);

      // Capture locations from simulation_started, state_update, and simulation_completed
      const isLocationEvent = ['simulation_started', 'state_update', 'simulation_completed'].includes(event.type);

      if (isLocationEvent && event.data?.location) {
        const locationKey = `${event.data.location.name}-${event.data.turn || 0}`;
        if (!seenLocations.has(locationKey)) {
          seenLocations.add(locationKey);
          const loc = {
            location: {
              place_name: event.data.location.name,
              lat: event.data.location.lat,
              lon: event.data.location.lon,
            },
            turn: event.data.turn || 0,
            timestamp: event.timestamp,
            stress_level: event.data.psychology?.stress || 0,
            action: event.data.last_action || '',
            thought: event.data.last_thought || '',
          };
          console.log('Adding location:', loc);
          locations.push(loc);
        }
      }
    });

    // If no locations from events yet but we have current location, add it
    if (locations.length === 0 && currentSimulation?.current_frame?.location) {
      console.log('No locations from events, using currentSimulation');
      locations.push({
        location: currentSimulation.current_frame.location,
        turn: currentSimulation.current_frame.turn || 0,
        timestamp: new Date().toISOString(),
        stress_level: currentSimulation.current_frame.psych_state?.stress || 0,
        action: '',
        thought: '',
      });
    }

    console.log('Final location history:', locations);
    return locations;
  }, [events, currentSimulation]);

  const handleCreateSimulation = async () => {
    try {
      clearEvents();
      const sim = await createSimulation({
        agent_name: agentName,
        starting_location: startingLocation,
        starting_stress: startingStress,
      });
      setSimulationId(sim.simulation_id);
    } catch (err) {
      console.error('Failed to create simulation:', err);
    }
  };

  const handleStartSimulation = async () => {
    if (!simulationId) return;
    try {
      await startSimulation(simulationId, maxTurns);
    } catch (err) {
      console.error('Failed to start simulation:', err);
    }
  };

  const handleStepSimulation = async () => {
    if (!simulationId) return;
    try {
      await stepSimulation(simulationId);
    } catch (err) {
      console.error('Failed to step simulation:', err);
    }
  };

  const handleViewHistory = async () => {
    if (!simulationId) return;
    try {
      await getHistory(simulationId);
    } catch (err) {
      console.error('Failed to get history:', err);
    }
  };

  const getEventIcon = (eventType: string) => {
    const icons: Record<string, string> = {
      connection_established: '🔌',
      simulation_started: '🚀',
      turn_start: '🔄',
      historical_event: '📜',
      agent_thinking: '🤔',
      agent_decision: '💭',
      action_executed: '⚡',
      state_update: '📊',
      simulation_completed: '✅',
    };
    return icons[eventType] || '📡';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-900 to-blue-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">🏛️ Historical Mind-Lab</h1>
          <p className="text-blue-100 mt-2">
            Multi-Agent Simulation Platform - Hou Jing Rebellion (548 CE)
          </p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* Create Simulation */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Create Simulation</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Agent Name
                  </label>
                  <input
                    type="text"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Starting Location
                  </label>
                  <select
                    value={startingLocation}
                    onChange={(e) => setStartingLocation(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="建康">建康 (Jiankang)</option>
                    <option value="江陵">江陵 (Jiangling)</option>
                    <option value="襄阳">襄阳 (Xiangyang)</option>
                    <option value="寿阳">寿阳 (Shouyang)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Starting Stress: {startingStress}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={startingStress}
                    onChange={(e) => setStartingStress(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={handleCreateSimulation}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                >
                  {loading ? 'Creating...' : '🆕 Create New Simulation'}
                </button>
              </div>
            </div>

            {/* Simulation Controls */}
            {simulationId && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-800">Simulation Controls</h2>

                <div className="space-y-3">
                  <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    <p className="font-mono break-all">ID: {simulationId}</p>
                    <p className="mt-1">
                      WebSocket: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Turns: {maxTurns}
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="50"
                      value={maxTurns}
                      onChange={(e) => setMaxTurns(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  <button
                    onClick={handleStartSimulation}
                    disabled={loading || currentSimulation?.status === 'completed' || currentSimulation?.status === 'running'}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                  >
                    {loading ? 'Starting...' :
                     currentSimulation?.status === 'completed' ? '✅ Completed' :
                     currentSimulation?.status === 'running' ? '🔄 Running...' :
                     '▶️ Start Simulation'}
                  </button>

                  <button
                    onClick={handleStepSimulation}
                    disabled={loading || currentSimulation?.status === 'completed'}
                    className="w-full bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 disabled:bg-gray-400 transition-colors"
                  >
                    {loading ? 'Stepping...' :
                     currentSimulation?.status === 'completed' ? '✅ Completed' :
                     '⏭️ Step (1 Turn)'}
                  </button>

                  <button
                    onClick={handleViewHistory}
                    disabled={loading}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                  >
                    {loading ? 'Loading...' : '📜 View History'}
                  </button>

                  {currentSimulation?.status === 'completed' && (
                    <div className="bg-green-50 border border-green-200 rounded-md p-3">
                      <p className="text-sm text-green-800 font-semibold">✅ Simulation Completed!</p>
                      <p className="text-xs text-green-600 mt-1">
                        Create a new simulation to run again.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Current State */}
            {currentSimulation && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-800">Current State</h2>

                <div className="space-y-3 text-sm">
                  <div>
                    <span className="font-semibold">Turn:</span> {currentSimulation.current_frame?.turn || 0}
                  </div>
                  <div>
                    <span className="font-semibold">Location:</span> {currentSimulation.current_frame?.location?.place_name || 'N/A'}
                  </div>
                  <div>
                    <span className="font-semibold">Stress:</span>{' '}
                    <span className={`font-bold ${
                      (currentSimulation.current_frame?.psych_state?.stress || 0) >= 80 ? 'text-red-600' :
                      (currentSimulation.current_frame?.psych_state?.stress || 0) >= 50 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {currentSimulation.current_frame?.psych_state?.stress || 0}/100
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold">Focus:</span> {currentSimulation.current_frame?.psych_state?.focus || 'N/A'}
                  </div>
                  <div>
                    <span className="font-semibold">Status:</span>{' '}
                    <span className={`px-2 py-1 rounded text-xs ${
                      currentSimulation.status === 'completed' ? 'bg-green-100 text-green-800' :
                      currentSimulation.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {currentSimulation.status}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
                <p className="font-semibold">Error:</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            )}
          </div>

          {/* Center Panel - Map */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-[500px]">
                <Map
                  currentLocation={currentSimulation?.current_frame?.location}
                  locationHistory={locationHistory}
                  className="rounded-lg"
                />
              </div>
            </div>

            {/* Event Feed */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">
                Real-Time Event Stream ({events.length})
              </h2>

              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {events.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    No events yet. Start a simulation to see events.
                  </p>
                ) : (
                  events.map((event: SimulationEvent, index: number) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-2xl">{getEventIcon(event.type)}</span>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-gray-800">{event.type}</span>
                            <span className="text-xs text-gray-500">
                              {new Date(event.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <pre className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">
                            {JSON.stringify(event.data, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* History Display */}
            {history.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-800">
                  Decision History ({history.length})
                </h2>

                <div className="space-y-4">
                  {history.map((decision, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-blue-500 pl-4 py-2"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-gray-800">Turn {decision.turn}</span>
                        <span className="text-sm text-gray-500">{decision.timestamp}</span>
                      </div>
                      <p className="text-sm text-gray-700 mb-1">
                        <span className="font-semibold">Location:</span> {decision.location}
                      </p>
                      <p className="text-sm text-gray-700 mb-1">
                        <span className="font-semibold">Event:</span> {decision.event_description}
                      </p>
                      <p className="text-sm text-gray-700 mb-1">
                        <span className="font-semibold">Thought:</span> {decision.agent_thought}
                      </p>
                      <p className="text-sm text-gray-700 mb-1">
                        <span className="font-semibold">Action:</span> {decision.action}
                      </p>
                      <p className="text-sm">
                        <span className="font-semibold">Stress:</span>{' '}
                        <span className={`font-bold ${
                          decision.stress_level >= 80 ? 'text-red-600' :
                          decision.stress_level >= 50 ? 'text-yellow-600' :
                          'text-green-600'
                        }`}>
                          {decision.stress_level}/100
                        </span>
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
