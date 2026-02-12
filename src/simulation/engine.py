"""Core simulation engine for Historical Mind-Lab.

This module provides a reusable, event-driven simulation engine that can be
used by both CLI and web service interfaces.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any, Callable, Awaitable

from src.domain.schemas import GeoPoint, PsychState, AgentProfile, SimulationFrame
from src.agents.prompts import render_istp_prompt, parse_llm_decision
from src.tools.archive import HistoricalArchive
from src.tools.gis import (
    calculate_distance,
    get_coordinates,
    get_route_info,
    format_route_description
)


class SimulationStatus(str, Enum):
    """Status of a simulation."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationEvent:
    """Represents an event emitted by the simulation.

    Attributes:
        type: Type of event (state_update, decision, action, completion, error).
        data: Event-specific data payload.
        timestamp: When the event occurred.
    """

    def __init__(self, event_type: str, data: Dict[str, Any]) -> None:
        """Initialize a simulation event.

        Args:
            event_type: Type of event.
            data: Event data.
        """
        self.type = event_type
        self.data = data
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the event.
        """
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class SimulationEngine:
    """Core simulation engine with event streaming support.

    Attributes:
        simulation_id: Unique identifier for this simulation.
        agent: The simulated historical figure.
        location: Current geographical position.
        psych_state: Current psychological state.
        inventory: Available resources.
        current_time: Simulation time.
        is_safe: Whether the agent has reached safety.
        history: Timeline of all simulation frames.
        status: Current simulation status.
        archive: Historical knowledge base.
        event_callback: Optional callback for event streaming.
    """

    def __init__(
        self,
        agent: AgentProfile,
        starting_location: str = "建康",
        starting_stress: int = 40,
        inventory: Optional[List[str]] = None,
        event_callback: Optional[Callable[[SimulationEvent], Awaitable[None]]] = None
    ) -> None:
        """Initialize simulation engine.

        Args:
            agent: Historical figure to simulate.
            starting_location: Ancient place name for starting location.
            starting_stress: Initial stress level (0-100).
            inventory: Starting resources.
            event_callback: Optional async callback for event streaming.
        """
        self.simulation_id = str(uuid.uuid4())
        self.agent = agent

        # Initialize location
        location = get_coordinates(starting_location)
        if not location:
            raise ValueError(f"Unknown starting location: {starting_location}")
        self.location = location

        # Initialize psychological state
        self.psych_state = PsychState(
            stress=starting_stress,
            focus="Family Safety",
            mbti="ISTP"
        )

        # Initialize inventory
        self.inventory = inventory or ["经书三卷", "银两若干", "家书", "短刀", "干粮（五日）"]

        # Simulation state
        self.current_time = datetime(548, 12, 15, 14, 0, 0)
        self.is_safe = False
        self.history: List[SimulationFrame] = []
        self.status = SimulationStatus.CREATED
        self.turn = 0
        self.max_turns = 10

        # Systems
        self.archive = HistoricalArchive()
        self.event_callback = event_callback

    async def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit a simulation event.

        Args:
            event_type: Type of event.
            data: Event data.
        """
        event = SimulationEvent(event_type, data)
        if self.event_callback:
            await self.event_callback(event)

    def get_state(self) -> Dict[str, Any]:
        """Get current simulation state as dictionary.

        Returns:
            Dictionary containing all simulation state.
        """
        danger = self.archive.assess_location_danger(
            self.location.place_name,
            self.current_time.year
        )

        return {
            "simulation_id": self.simulation_id,
            "status": self.status.value,
            "turn": self.turn,
            "agent": {
                "name": self.agent.name,
                "birth_year": self.agent.birth_year,
                "traits": self.agent.traits
            },
            "location": {
                "name": self.location.place_name,
                "lat": self.location.lat,
                "lon": self.location.lon,
                "danger_level": danger["level"]
            },
            "psychology": {
                "stress": self.psych_state.stress,
                "focus": self.psych_state.focus,
                "mbti": self.psych_state.mbti
            },
            "inventory": self.inventory,
            "current_time": self.current_time.isoformat(),
            "is_safe": self.is_safe,
            "decisions_made": len(self.history)
        }

    def _get_historical_context(self) -> str:
        """Build historical context for prompts."""
        search_results = self.archive.search_historical_context(
            year=self.current_time.year,
            location=self.location.place_name,
            month=self.current_time.month
        )

        danger_info = self.archive.assess_location_danger(
            self.location.place_name,
            self.current_time.year
        )

        context_lines = ["## 历史背景 (Historical Context)\n"]
        context_lines.append(f"**当前位置危险度:** {danger_info['level']}/100")
        context_lines.append(f"**评估:** {danger_info['reasoning']}\n")

        if search_results["events"]:
            context_lines.append("**近期事件:**")
            for event in search_results["events"][:3]:
                date_str = f"{event['year']}年{event.get('month', '?')}月"
                context_lines.append(
                    f"- {date_str}: {event['title']} (威胁度: {event['threat_level']}/100)"
                )
                context_lines.append(f"  {event['description'][:100]}...")
            context_lines.append("")

        nearby_safe = [loc for loc in search_results["locations"] if loc.get("danger_level", 100) < 50]
        if nearby_safe:
            context_lines.append("**可能的避难地点:**")
            for loc in nearby_safe[:2]:
                context_lines.append(f"- {loc['ancient_name']}: 危险度 {loc['danger_level']}/100")
            context_lines.append("")

        return "\n".join(context_lines)

    def _get_route_options(self) -> str:
        """Get formatted route options."""
        destinations = {
            "建康": ["江陵", "寻阳", "襄阳"],
            "台城": ["秦淮河", "建康"],
            "秦淮河": ["江陵", "寻阳"],
        }

        dest_names = destinations.get(self.location.place_name, ["江陵", "寻阳"])
        route_info = "\n## 可能的撤离路线 (Escape Routes)\n\n"

        for dest in dest_names[:3]:
            try:
                route = get_route_info(self.location.place_name, dest)
                route_info += format_route_description(route) + "\n\n"
            except ValueError:
                continue

        return route_info

    async def _mock_llm_call(self, prompt: str, stress_level: int) -> str:
        """Mock LLM call for MVP."""
        await asyncio.sleep(0.3)

        if "江陵" in prompt and stress_level >= 70:
            return """{
  "reasoning": "台城已陷，火光逼近。根据历史情报，江陵在萧绎控制下相对安全。水路约5日可达，必须立即撤离。",
  "next_action": "move_to:江陵"
}"""
        elif "寻阳" in prompt and stress_level >= 60:
            return """{
  "reasoning": "建康已失，但寻阳距离较近，水路仅需3日。可先至寻阳观望局势，再决定是否继续西行。",
  "next_action": "move_to:寻阳"
}"""
        elif stress_level >= 50:
            return """{
  "reasoning": "当前威胁尚可控，但形势严峻。应立即收集更多情报，确认最佳撤离路线。",
  "next_action": "gather_intel"
}"""
        else:
            return """{
  "reasoning": "局势虽有动荡，但尚未直接威胁。可先派家仆探查各方消息，暂时留守观察。",
  "next_action": "wait:observe_situation"
}"""

    async def _execute_action(self, action: str) -> Dict[str, Any]:
        """Execute an action and return result data."""
        result = {"action": action, "success": True}

        if action.startswith("move_to:"):
            destination_name = action.split(":", 1)[1]
            destination = get_coordinates(destination_name)

            if destination:
                try:
                    route = get_route_info(self.location.place_name, destination_name)
                    result["route"] = {
                        "distance_km": route["distance_km"],
                        "direction": route["direction"],
                        "travel_time_hours": route["travel_time_boat"]
                    }

                    old_location = self.location.place_name
                    self.location = destination

                    danger_info = self.archive.assess_location_danger(
                        destination_name,
                        self.current_time.year
                    )

                    if danger_info["level"] < 40:
                        self.psych_state.stress = max(0, self.psych_state.stress - 30)
                        self.is_safe = True
                        result["reached_safety"] = True
                    else:
                        self.psych_state.stress = max(0, self.psych_state.stress - 10)
                        result["reached_safety"] = False

                    travel_hours = int(route["travel_time_boat"])
                    self.current_time += timedelta(hours=travel_hours)

                    result["old_location"] = old_location
                    result["new_location"] = destination_name

                except ValueError as e:
                    result["success"] = False
                    result["error"] = str(e)

        elif action == "gather_intel":
            self.psych_state.stress = max(0, self.psych_state.stress - 5)
            self.current_time += timedelta(hours=2)

        elif action == "seek_shelter":
            self.psych_state.stress = max(0, self.psych_state.stress - 10)
            self.current_time += timedelta(hours=1)

        elif action.startswith("wait:"):
            self.current_time += timedelta(hours=2)

        elif action.startswith("interact:"):
            self.psych_state.stress = max(0, self.psych_state.stress - 5)
            self.current_time += timedelta(hours=1)

        return result

    async def step(self) -> Dict[str, Any]:
        """Execute one simulation step.

        Returns:
            Step result dictionary.
        """
        self.turn += 1

        # Emit turn start event
        await self.emit_event("turn_start", {
            "turn": self.turn,
            "state": self.get_state()
        })

        # Get historical event
        historical_events = self.archive.get_events_by_date(548, month=12)
        if self.turn <= len(historical_events):
            event_data = historical_events[self.turn - 1]
            event_desc = f"【{event_data['title']}】{event_data['description']}"
            threat_level = event_data["threat_level"]
        else:
            event_desc = "局势持续动荡，需保持警惕。"
            threat_level = 20

        # Emit event
        await self.emit_event("historical_event", {
            "description": event_desc,
            "threat_level": threat_level
        })

        # Update stress
        self.psych_state.stress = min(100, self.psych_state.stress + threat_level)

        # Build prompt
        historical_context = self._get_historical_context()
        route_info = self._get_route_options() if self.psych_state.stress > 50 else ""
        enhanced_threats = f"{event_desc}\n\n{historical_context}{route_info}"

        prompt = render_istp_prompt(
            current_location=f"{self.location.place_name} ({self.location.lat:.4f}, {self.location.lon:.4f})",
            external_threats=enhanced_threats,
            inventory=", ".join(self.inventory),
            stress_level=self.psych_state.stress
        )

        # Emit thinking event
        await self.emit_event("agent_thinking", {
            "stress": self.psych_state.stress,
            "location": self.location.place_name
        })

        # Get decision
        llm_response = await self._mock_llm_call(prompt, self.psych_state.stress)
        decision = parse_llm_decision(llm_response)

        # Emit decision event
        await self.emit_event("agent_decision", {
            "reasoning": decision["reasoning"],
            "action": decision["next_action"]
        })

        # Record frame
        frame = SimulationFrame(
            timestamp=self.current_time,
            agent_state=self.agent,
            action=decision["next_action"],
            thought_process=decision["reasoning"]
        )
        self.history.append(frame)

        # Execute action
        action_result = await self._execute_action(decision["next_action"])

        # Emit action result
        await self.emit_event("action_executed", action_result)

        # Emit state update
        await self.emit_event("state_update", self.get_state())

        return {
            "turn": self.turn,
            "event": event_desc,
            "decision": decision,
            "action_result": action_result,
            "state": self.get_state()
        }

    async def run(self) -> Dict[str, Any]:
        """Run the simulation to completion.

        Returns:
            Final simulation result.
        """
        self.status = SimulationStatus.RUNNING
        await self.emit_event("simulation_started", self.get_state())

        try:
            while not self.is_safe and self.turn < self.max_turns:
                await self.step()

            self.status = SimulationStatus.COMPLETED
            await self.emit_event("simulation_completed", self.get_state())

            return {
                "status": "completed",
                "final_state": self.get_state(),
                "total_turns": self.turn,
                "reached_safety": self.is_safe
            }

        except Exception as e:
            self.status = SimulationStatus.FAILED
            await self.emit_event("simulation_error", {
                "error": str(e),
                "turn": self.turn
            })
            raise
