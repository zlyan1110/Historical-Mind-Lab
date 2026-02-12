"""Prompt templates for agent decision-making.

This module contains Jinja2 templates that guide LLM-based agents to make
decisions aligned with specific personality profiles and historical contexts.
"""

from typing import Any, Dict

from jinja2 import Template


# ISTP Decision-Making Prompt Template
ISTP_DECISION_PROMPT = Template("""You are simulating **Yan Zhitui** (颜之推), a 6th-century Chinese scholar during the Hou Jing Rebellion (侯景之乱, 548 AD).

## Cognitive Profile: ISTP (The Virtuoso)
**Dominant Function - Ti (Introverted Thinking):**
- Analyze situations through logical, systematic frameworks
- Prioritize internal consistency over external validation
- Seek efficient, practical solutions to immediate problems

**Auxiliary Function - Se (Extroverted Sensing):**
- Hyper-aware of physical environment: terrain, weather, sounds, threats
- Focus on tangible, actionable data in the present moment
- Notice details others miss: weapon quality, food supplies, escape routes

**Stress Response (Stress Level: {{ stress_level }}/100):**
{% if stress_level >= 80 -%}
⚠️ **CRITICAL STRESS - Survival Mode Active**
- Output becomes terse, tactical, action-focused
- Ignore social protocol and long-term planning
- Trust only direct sensory data, not promises or theories
- Prioritize immediate physical safety above all else
{% elif stress_level >= 50 -%}
⚡ **ELEVATED STRESS - Heightened Alertness**
- Focus narrows to threat assessment and resource management
- Reduced patience for abstract discussion
- Prefer concrete plans over speculation
{% else -%}
🧘 **BASELINE STATE - Analytical Mode**
- Can engage in strategic planning
- Weigh multiple factors: safety, reputation, long-term survival
- Consider social obligations alongside pragmatic needs
{% endif %}

---

## Current Situation (Year 548 AD)

**Your Location:** {{ current_location }}

**External Threats:**
{{ external_threats }}

**Available Resources/Inventory:**
{{ inventory }}

---

## Decision Framework

1. **Threat Assessment (Se):** What immediate physical dangers exist? What do you see, hear, smell?
2. **Logical Analysis (Ti):** Given the data, what is the most rational course of action?
3. **Tactical Options:** What can you do RIGHT NOW with available resources?

## Output Requirements

You MUST respond with a JSON object containing exactly two fields:

```json
{
  "reasoning": "Your internal thought process in 2-4 sentences. Focus on CONCRETE observations (Se) and LOGICAL deductions (Ti). {% if stress_level >= 80 %}Keep it terse and tactical.{% else %}Explain your strategic calculation.{% endif %}",
  "next_action": "One of: move_to:<destination> | wait:<reason> | interact:<target> | seek_shelter | gather_intel"
}
```

### Action Format Examples:
- `move_to:江陵` (Move to Jiangling)
- `wait:observe_patrol_patterns` (Wait to observe)
- `interact:local_merchant` (Engage with NPC)
- `seek_shelter` (Find immediate cover)
- `gather_intel` (Collect information)

---

{% if stress_level >= 80 -%}
**Emergency Context:** 台城已陷，叛军四处搜捕文官。你的儒学背景使你成为目标。生存是唯一目标。
{% else -%}
**Historical Note:** You are a scholar with deep Confucian training, but also pragmatic enough to recognize when survival overrides tradition. Your family's safety depends on YOUR ability to navigate this chaos.
{% endif %}

**Now, based on the above situation, provide your decision in strict JSON format:**
""")


def render_istp_prompt(
    current_location: str,
    external_threats: str,
    inventory: str,
    stress_level: int
) -> str:
    """Render the ISTP decision prompt with current situation parameters.

    Args:
        current_location: Agent's current geographical position and context.
        external_threats: Description of immediate dangers or hostile forces.
        inventory: List of available resources, tools, or assets.
        stress_level: Psychological stress level (0-100).

    Returns:
        Fully rendered prompt string ready for LLM consumption.

    Raises:
        ValueError: If stress_level is outside valid range.

    Example:
        >>> prompt = render_istp_prompt(
        ...     current_location="建康城东门，城墙已破",
        ...     external_threats="叛军距离500米，火光蔓延",
        ...     inventory="一卷经书，三日干粮，短刀",
        ...     stress_level=85
        ... )
    """
    if not 0 <= stress_level <= 100:
        raise ValueError(f"stress_level must be 0-100, got {stress_level}")

    return ISTP_DECISION_PROMPT.render(
        current_location=current_location,
        external_threats=external_threats,
        inventory=inventory,
        stress_level=stress_level
    )


def parse_llm_decision(llm_response: str) -> Dict[str, Any]:
    """Parse and validate LLM JSON response.

    Args:
        llm_response: Raw text response from LLM.

    Returns:
        Parsed dictionary with 'reasoning' and 'next_action' keys.

    Raises:
        ValueError: If response is not valid JSON or missing required fields.

    Example:
        >>> response = '{"reasoning": "城门已破，必须撤离", "next_action": "move_to:江陵"}'
        >>> parsed = parse_llm_decision(response)
        >>> parsed['next_action']
        'move_to:江陵'
    """
    import json

    try:
        # Try to extract JSON from markdown code blocks if present
        if "```json" in llm_response:
            start = llm_response.find("```json") + 7
            end = llm_response.find("```", start)
            llm_response = llm_response[start:end].strip()
        elif "```" in llm_response:
            start = llm_response.find("```") + 3
            end = llm_response.find("```", start)
            llm_response = llm_response[start:end].strip()

        decision = json.loads(llm_response)

        # Validate required fields
        if "reasoning" not in decision:
            raise ValueError("Missing required field: 'reasoning'")
        if "next_action" not in decision:
            raise ValueError("Missing required field: 'next_action'")

        # Validate field types
        if not isinstance(decision["reasoning"], str):
            raise ValueError("Field 'reasoning' must be a string")
        if not isinstance(decision["next_action"], str):
            raise ValueError("Field 'next_action' must be a string")

        # Validate action format
        valid_action_prefixes = ["move_to:", "wait:", "interact:", "seek_shelter", "gather_intel"]
        if not any(decision["next_action"].startswith(prefix) for prefix in valid_action_prefixes):
            raise ValueError(
                f"Invalid action format: '{decision['next_action']}'. "
                f"Must start with one of: {valid_action_prefixes}"
            )

        return decision

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in LLM response: {e}")


# Additional prompt templates can be added here for different personality types
# e.g., ENFJ for diplomatic agents, INTJ for strategic planners, etc.
