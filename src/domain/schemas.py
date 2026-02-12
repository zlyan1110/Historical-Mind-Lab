"""Domain models for Historical Mind-Lab simulation.

This module defines the core Pydantic models used throughout the simulation,
including geographical coordinates, psychological states, agent profiles,
and simulation frames.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator


class GeoPoint(BaseModel):
    """Represents a geographical point with coordinates and location name.

    Attributes:
        lat: Latitude in decimal degrees (-90 to 90).
        lon: Longitude in decimal degrees (-180 to 180).
        place_name: Human-readable name of the location (e.g., "Jiankang").
    """

    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    place_name: str = Field(..., min_length=1, description="Name of the location")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "lat": 32.0583,
                    "lon": 118.7966,
                    "place_name": "Jiankang"
                }
            ]
        }
    }


class PsychState(BaseModel):
    """Represents the psychological state of an agent.

    This model captures the cognitive and emotional state using MBTI framework
    and stress levels, enabling personality-driven decision-making.

    Attributes:
        stress: Stress level from 0 (calm) to 100 (extreme distress).
        focus: Current cognitive priority (e.g., "Survival", "Social", "Planning").
        mbti: Myers-Briggs Type Indicator (e.g., "ISTP" for Yan Zhitui).
    """

    stress: int = Field(..., ge=0, le=100, description="Stress level (0-100)")
    focus: str = Field(..., min_length=1, description="Current cognitive priority")
    mbti: str = Field(..., min_length=4, max_length=4, description="MBTI personality type")

    @field_validator("mbti")
    @classmethod
    def validate_mbti(cls, v: str) -> str:
        """Validate MBTI string format.

        Args:
            v: The MBTI string to validate.

        Returns:
            The validated MBTI string in uppercase.

        Raises:
            ValueError: If MBTI string is invalid.
        """
        v = v.upper()
        valid_chars = {
            0: ["E", "I"],
            1: ["S", "N"],
            2: ["T", "F"],
            3: ["J", "P"]
        }

        if len(v) != 4:
            raise ValueError("MBTI must be exactly 4 characters")

        for i, char in enumerate(v):
            if char not in valid_chars[i]:
                raise ValueError(
                    f"Invalid MBTI character '{char}' at position {i}. "
                    f"Expected one of {valid_chars[i]}"
                )

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stress": 85,
                    "focus": "Survival",
                    "mbti": "ISTP"
                }
            ]
        }
    }


class AgentProfile(BaseModel):
    """Represents a historical agent's biographical profile.

    This model stores the core identity and characteristics of a simulated
    historical figure.

    Attributes:
        name: Full name of the agent (e.g., "Yan Zhitui").
        birth_year: Year of birth in CE (e.g., 531 for Yan Zhitui).
        traits: List of personality or behavioral traits.
    """

    name: str = Field(..., min_length=1, description="Full name of the agent")
    birth_year: int = Field(..., gt=0, description="Year of birth in CE")
    traits: List[str] = Field(default_factory=list, description="Personality traits")

    @field_validator("traits")
    @classmethod
    def validate_traits(cls, v: List[str]) -> List[str]:
        """Ensure all traits are non-empty strings.

        Args:
            v: List of trait strings.

        Returns:
            The validated list of traits.

        Raises:
            ValueError: If any trait is empty.
        """
        for trait in v:
            if not trait or not trait.strip():
                raise ValueError("All traits must be non-empty strings")
        return [trait.strip() for trait in v]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Yan Zhitui",
                    "birth_year": 531,
                    "traits": ["Analytical", "Pragmatic", "Observant"]
                }
            ]
        }
    }


class SimulationFrame(BaseModel):
    """Represents a single frame in the simulation timeline.

    Each frame captures the agent's state, decision, and reasoning at a specific
    moment in time, forming a complete audit trail of the simulation.

    Attributes:
        timestamp: When this frame occurred in simulation time.
        agent_state: The agent's profile at this moment.
        action: The action taken (e.g., "move_to:江陵", "wait", "seek_shelter").
        thought_process: Internal reasoning that led to the action.
    """

    timestamp: datetime = Field(..., description="Simulation timestamp")
    agent_state: AgentProfile = Field(..., description="Agent profile snapshot")
    action: str = Field(..., min_length=1, description="Action taken by agent")
    thought_process: str = Field(..., min_length=1, description="Agent's reasoning")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "timestamp": "548-12-15T14:30:00",
                    "agent_state": {
                        "name": "Yan Zhitui",
                        "birth_year": 531,
                        "traits": ["Analytical"]
                    },
                    "action": "move_to:江陵",
                    "thought_process": "台城已失守，必须向西撤离至江陵以避战火。"
                }
            ]
        }
    }
