"""Enhanced CLI simulation loop with historical search and GIS integration.

This module implements an intelligent simulation loop that uses:
- Historical archive for real event data
- GIS tools for spatial awareness and route planning
- Context-aware prompt generation
- Realistic agent decision-making
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from src.domain.schemas import GeoPoint, PsychState, AgentProfile, SimulationFrame
from src.agents.prompts import render_istp_prompt, parse_llm_decision
from src.tools.archive import HistoricalArchive
from src.tools.gis import (
    calculate_distance,
    get_coordinates,
    get_route_info,
    format_route_description
)


class SimulationState:
    """Tracks the current state of the simulation.

    Attributes:
        agent: The simulated historical figure.
        location: Current geographical position.
        psych_state: Current psychological state.
        inventory: Available resources.
        current_time: Simulation time.
        is_safe: Whether the agent has reached safety.
        history: Timeline of all simulation frames.
        archive: Historical knowledge base.
    """

    def __init__(
        self,
        agent: AgentProfile,
        location: GeoPoint,
        psych_state: PsychState,
        inventory: List[str]
    ) -> None:
        """Initialize simulation state.

        Args:
            agent: Historical figure being simulated.
            location: Starting location.
            psych_state: Initial psychological state.
            inventory: Starting resources.
        """
        self.agent = agent
        self.location = location
        self.psych_state = psych_state
        self.inventory = inventory
        self.current_time = datetime(548, 12, 15, 14, 0, 0)  # Dec 15, 548 AD, 2 PM
        self.is_safe = False
        self.history: List[SimulationFrame] = []
        self.archive = HistoricalArchive()

    def add_frame(self, action: str, thought: str) -> None:
        """Record a decision frame in the simulation history.

        Args:
            action: The action taken by the agent.
            thought: The agent's reasoning process.
        """
        frame = SimulationFrame(
            timestamp=self.current_time,
            agent_state=self.agent,
            action=action,
            thought_process=thought
        )
        self.history.append(frame)


def get_historical_context(state: SimulationState) -> str:
    """Build historical context string for LLM prompt.

    Args:
        state: Current simulation state.

    Returns:
        Formatted historical context with events, locations, and survival tips.
    """
    # Search for events at current location and time
    search_results = state.archive.search_historical_context(
        year=state.current_time.year,
        location=state.location.place_name,
        month=state.current_time.month
    )

    # Get danger assessment for current location
    danger_info = state.archive.assess_location_danger(
        state.location.place_name,
        state.current_time.year
    )

    context_lines = ["## 历史背景 (Historical Context)\n"]

    # Current location danger
    context_lines.append(f"**当前位置危险度:** {danger_info['level']}/100")
    context_lines.append(f"**评估:** {danger_info['reasoning']}\n")

    # Recent events
    if search_results["events"]:
        context_lines.append("**近期事件:**")
        for event in search_results["events"][:3]:  # Limit to 3 most relevant
            date_str = f"{event['year']}年{event.get('month', '?')}月"
            context_lines.append(
                f"- {date_str}: {event['title']} (威胁度: {event['threat_level']}/100)"
            )
            context_lines.append(f"  {event['description'][:100]}...")
        context_lines.append("")

    # Nearby safe locations
    nearby_safe = []
    for loc in search_results["locations"]:
        if loc.get("danger_level", 100) < 50:
            nearby_safe.append(loc)

    if nearby_safe:
        context_lines.append("**可能的避难地点:**")
        for loc in nearby_safe[:2]:  # Top 2 safe locations
            context_lines.append(
                f"- {loc['ancient_name']}: 危险度 {loc['danger_level']}/100"
            )
        context_lines.append("")

    # Survival tips
    if search_results["survival_tips"]:
        context_lines.append("**生存建议:**")
        for tip in search_results["survival_tips"][:2]:
            context_lines.append(f"- {tip['advice'][:80]}...")
        context_lines.append("")

    return "\n".join(context_lines)


def get_route_options(current_location: str) -> List[Dict[str, Any]]:
    """Get possible escape routes from current location.

    Args:
        current_location: Current ancient place name.

    Returns:
        List of route information dictionaries.
    """
    # Define potential destinations based on historical knowledge
    destinations = {
        "建康": ["江陵", "寻阳", "襄阳"],
        "台城": ["秦淮河", "建康"],
        "秦淮河": ["江陵", "寻阳"],
    }

    dest_names = destinations.get(current_location, ["江陵", "寻阳"])
    routes = []

    for dest in dest_names:
        try:
            route = get_route_info(current_location, dest)
            routes.append(route)
        except ValueError:
            # Destination not in database, skip
            continue

    return routes


def build_enhanced_prompt(state: SimulationState, event_description: str) -> str:
    """Build enhanced prompt with historical context and route information.

    Args:
        state: Current simulation state.
        event_description: Description of triggering event.

    Returns:
        Complete prompt string for LLM.
    """
    # Get historical context
    historical_context = get_historical_context(state)

    # Get route options if in a dangerous location
    route_info = ""
    if state.psych_state.stress > 50:
        routes = get_route_options(state.location.place_name)
        if routes:
            route_info = "\n## 可能的撤离路线 (Escape Routes)\n\n"
            for route in routes[:3]:  # Top 3 routes
                route_info += format_route_description(route) + "\n\n"

    # Build complete context
    enhanced_threats = f"{event_description}\n\n{historical_context}{route_info}"

    # Render prompt with enhanced context
    prompt = render_istp_prompt(
        current_location=f"{state.location.place_name} ({state.location.lat:.4f}, {state.location.lon:.4f})",
        external_threats=enhanced_threats,
        inventory=", ".join(state.inventory),
        stress_level=state.psych_state.stress
    )

    return prompt


async def mock_llm_call(prompt: str, stress_level: int) -> str:
    """Simulate an LLM API call with realistic delays.

    Args:
        prompt: The rendered prompt.
        stress_level: Current stress level to determine response style.

    Returns:
        Mock JSON response string.
    """
    # Simulate API latency
    await asyncio.sleep(0.5)

    # Extract route information from prompt to make intelligent decisions
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


async def execute_action(state: SimulationState, action: str) -> None:
    """Execute agent's decided action and update state.

    Args:
        state: Current simulation state.
        action: Action string to execute.
    """
    if action.startswith("move_to:"):
        destination_name = action.split(":", 1)[1]
        print(f"🚶 [Action] Moving to {destination_name}...")

        # Get destination coordinates
        destination = get_coordinates(destination_name)
        if destination:
            # Calculate route info
            try:
                route = get_route_info(state.location.place_name, destination_name)

                # Show route details
                print(f"   Route: {format_route_description(route)}")
                print()

                # Update location
                old_location = state.location.place_name
                state.location = destination

                # Update stress based on destination safety
                danger_info = state.archive.assess_location_danger(
                    destination_name,
                    state.current_time.year
                )

                # Reduce stress if moving to safer location
                if danger_info["level"] < 40:
                    state.psych_state.stress = max(0, state.psych_state.stress - 30)
                    state.is_safe = True  # Reached safe haven
                    print(f"   ✓ Reached safe haven! Stress reduced to {state.psych_state.stress}")
                else:
                    state.psych_state.stress = max(0, state.psych_state.stress - 10)
                    print(f"   → Stress reduced to {state.psych_state.stress}")

                # Advance time based on travel
                travel_hours = int(route["travel_time_boat"])
                state.current_time += timedelta(hours=travel_hours)

            except ValueError as e:
                print(f"   ⚠️  Navigation error: {e}")

    elif action == "gather_intel":
        print("🔍 [Action] Gathering intelligence...")
        print("   Consulting local merchants and observing patrol patterns...")
        state.psych_state.stress = max(0, state.psych_state.stress - 5)
        state.current_time += timedelta(hours=2)

    elif action == "seek_shelter":
        print("🏠 [Action] Seeking immediate shelter...")
        state.psych_state.stress = max(0, state.psych_state.stress - 10)
        state.current_time += timedelta(hours=1)

    elif action.startswith("wait:"):
        reason = action.split(":", 1)[1]
        print(f"⏳ [Action] Waiting: {reason}")
        state.current_time += timedelta(hours=2)

    elif action.startswith("interact:"):
        target = action.split(":", 1)[1]
        print(f"💬 [Action] Interacting with: {target}")
        state.psych_state.stress = max(0, state.psych_state.stress - 5)
        state.current_time += timedelta(hours=1)


def print_frame(state: SimulationState, turn: int) -> None:
    """Print the current simulation frame to console.

    Args:
        state: Current simulation state.
        turn: Turn number.
    """
    print("\n" + "=" * 100)
    print(f"Turn {turn} | {state.current_time.strftime('%Y年%m月%d日 %H:%M')}")
    print("=" * 100)
    print(f"📍 Location: {state.location.place_name} ({state.location.lat:.4f}, {state.location.lon:.4f})")

    # Show danger level
    danger = state.archive.assess_location_danger(
        state.location.place_name,
        state.current_time.year
    )
    danger_emoji = "🟢" if danger["level"] < 30 else "🟡" if danger["level"] < 70 else "🔴"
    print(f"{danger_emoji} Danger: {danger['level']}/100 - {danger['reasoning'][:50]}...")

    print(f"🧠 Stress: {state.psych_state.stress}/100 | Focus: {state.psych_state.focus} | MBTI: {state.psych_state.mbti}")
    print(f"🎒 Inventory: {', '.join(state.inventory)}")

    if state.history:
        latest = state.history[-1]
        print(f"\n💭 Thought: {latest.thought_process}")
        print(f"⚡ Decision: {latest.action}")


async def main() -> None:
    """Main simulation loop entry point."""

    print("\n" + "🏛️" * 40)
    print("HISTORICAL MIND-LAB: Enhanced Yan Zhitui Simulation")
    print("With Historical Knowledge Base & GIS Navigation")
    print("🏛️" * 40 + "\n")

    # Initialize Yan Zhitui in Jiankang
    yan_zhitui = AgentProfile(
        name="颜之推 (Yan Zhitui)",
        birth_year=531,
        traits=["Analytical", "Pragmatic", "Observant", "Scholarly"]
    )

    jiankang = get_coordinates("建康")
    if not jiankang:
        print("❌ Error: Could not geocode starting location")
        return

    psych_state = PsychState(
        stress=40,
        focus="Family Safety",
        mbti="ISTP"
    )

    inventory = ["经书三卷", "银两若干", "家书", "短刀", "干粮（五日）"]

    state = SimulationState(
        agent=yan_zhitui,
        location=jiankang,
        psych_state=psych_state,
        inventory=inventory
    )

    print("📚 [System] Loading historical archive...")
    print(f"   Loaded {len(state.archive.data.get('events', []))} historical events")
    print(f"   Loaded {len(state.archive.data.get('locations', []))} locations")
    print(f"   Time period: 548-552 CE (Hou Jing Rebellion)")

    print("\n🗺️  [System] Initializing GIS navigation...")
    print(f"   Geocoding database: 15+ ancient locations")
    print(f"   Navigation: Haversine distance + bearing calculation")

    print("\n📜 [System] Initializing simulation state...")
    print_frame(state, 0)

    # Simulation loop with historical event triggers
    turn = 0
    max_turns = 10

    # Get real historical events from archive
    historical_events = state.archive.get_events_by_date(548, month=12)

    while not state.is_safe and turn < max_turns:
        turn += 1

        # Get appropriate historical event if available
        if turn <= len(historical_events):
            event_data = historical_events[turn - 1]
            event_desc = f"【{event_data['title']}】{event_data['description']}"
            threat_level = event_data["threat_level"]
        else:
            # Fallback generic event
            event_desc = "局势持续动荡，需保持警惕。"
            threat_level = 20

        print(f"\n\n🔔 [Event] {event_desc}")
        print(f"   Threat Level: {threat_level}/100")

        # Update stress based on event
        state.psych_state.stress = min(100, state.psych_state.stress + threat_level)

        # Build enhanced prompt with historical context and route info
        prompt = build_enhanced_prompt(state, event_desc)

        # Call LLM (mocked for now)
        print(f"🤖 [LLM] Consulting ISTP decision engine (stress={state.psych_state.stress})...")
        llm_response = await mock_llm_call(prompt, state.psych_state.stress)

        # Parse response
        decision = parse_llm_decision(llm_response)

        # Record the decision
        state.add_frame(
            action=decision["next_action"],
            thought=decision["reasoning"]
        )

        # Execute action
        await execute_action(state, decision["next_action"])

        # Print updated frame
        print_frame(state, turn)

        # Dramatic pause for readability
        await asyncio.sleep(1)

    # Final summary
    print("\n\n" + "🎬" * 40)
    if state.is_safe:
        print("✅ SIMULATION COMPLETE: Agent reached safety!")
        print(f"   Final destination: {state.location.place_name}")
        print(f"   Final stress level: {state.psych_state.stress}/100")
    else:
        print("⏱️  SIMULATION TIMEOUT: Maximum turns reached.")
        print(f"   Current location: {state.location.place_name}")
        print(f"   Agent survival status: {'Safe' if state.psych_state.stress < 70 else 'At Risk'}")
    print("🎬" * 40 + "\n")

    print(f"📊 Final Statistics:")
    print(f"   Total Turns: {turn}")
    print(f"   Total Distance Traveled: ", end="")

    # Calculate total distance
    if len(state.history) > 0:
        total_distance = 0
        prev_location = get_coordinates("建康")
        for frame in state.history:
            if frame.action.startswith("move_to:"):
                dest_name = frame.action.split(":", 1)[1]
                dest = get_coordinates(dest_name)
                if dest and prev_location:
                    total_distance += calculate_distance(prev_location, dest)
                    prev_location = dest
        print(f"{total_distance:.1f} km")
    else:
        print("0 km")

    print(f"   Decisions Made: {len(state.history)}")
    print(f"   Simulation Duration: {(state.current_time - datetime(548, 12, 15, 14, 0, 0)).days} days")

    print("\n📖 Decision Timeline:")
    for i, frame in enumerate(state.history, 1):
        time_str = frame.timestamp.strftime('%m月%d日 %H:%M')
        print(f"   {i}. [{time_str}] {frame.action}")
        print(f"      思考: {frame.thought_process[:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
