/**
 * Type definitions for Historical Mind-Lab simulation
 */

export interface GeoPoint {
  lat: number;
  lon: number;
  place_name: string;
}

export interface PsychState {
  stress: number;
  focus: string;
  mbti: string;
}

export interface AgentProfile {
  name: string;
  birth_year: number;
  personality_type: string;
  core_values: string[];
  background: string;
}

export interface SimulationFrame {
  turn: number;
  timestamp: string;
  location: GeoPoint;
  psych_state: PsychState;
  inventory: string[];
  recent_events: string[];
}

export interface SimulationState {
  simulation_id: string;
  agent: AgentProfile;
  current_frame: SimulationFrame;
  status: string;
  created_at: string;
}

export interface SimulationEvent {
  type: string;
  timestamp: string;
  data: any;
}

export interface CreateSimulationRequest {
  agent_name: string;
  starting_location: string;
  starting_stress?: number;
  initial_inventory?: string[];
}

export interface Decision {
  turn: number;
  timestamp: string;
  location: string;
  event_description: string;
  agent_thought: string;
  action: string;
  stress_level: number;
}
