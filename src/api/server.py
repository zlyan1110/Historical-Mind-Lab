"""FastAPI server for Historical Mind-Lab simulation service.

This module provides HTTP REST endpoints for creating and managing simulations.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.domain.schemas import AgentProfile
from src.simulation.engine import SimulationEngine, SimulationStatus
from src.api.websocket import router as websocket_router, create_streaming_callback


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateSimulationRequest(BaseModel):
    """Request model for creating a new simulation."""

    agent_name: str = Field(default="颜之推 (Yan Zhitui)", description="Name of the historical figure")
    birth_year: int = Field(default=531, description="Birth year of the agent")
    traits: List[str] = Field(
        default=["Analytical", "Pragmatic", "Observant", "Scholarly"],
        description="Personality traits"
    )
    starting_location: str = Field(default="建康", description="Ancient place name for starting location")
    starting_stress: int = Field(default=40, ge=0, le=100, description="Initial stress level")
    inventory: Optional[List[str]] = Field(
        default=None,
        description="Starting inventory items"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "agent_name": "颜之推 (Yan Zhitui)",
                    "birth_year": 531,
                    "traits": ["Analytical", "Pragmatic", "Observant"],
                    "starting_location": "建康",
                    "starting_stress": 40,
                    "inventory": ["经书三卷", "银两若干", "家书"]
                }
            ]
        }
    }


class SimulationResponse(BaseModel):
    """Response model for simulation data."""

    simulation_id: str
    status: str
    turn: int
    agent: Dict
    location: Dict
    psychology: Dict
    inventory: List[str]
    current_time: str
    is_safe: bool
    decisions_made: int


class SimulationListItem(BaseModel):
    """Response model for simulation list item."""

    simulation_id: str
    status: str
    agent_name: str
    current_location: str
    turn: int
    created_at: str


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Historical Mind-Lab API",
    description="Multi-Agent simulation platform for historical decision-making",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router
app.include_router(websocket_router)

# In-memory storage for simulations (use Redis in production)
simulations: Dict[str, Dict] = {}
simulation_engines: Dict[str, SimulationEngine] = {}


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Historical Mind-Lab API",
        "version": "1.0.0",
        "description": "Multi-Agent simulation platform for historical decision-making",
        "endpoints": {
            "docs": "/docs",
            "simulations": "/simulations",
            "websocket": "/ws/simulations/{id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_simulations": len([s for s in simulations.values() if s["status"] == "running"])
    }


@app.post("/simulations", response_model=SimulationResponse, status_code=201)
async def create_simulation(
    request: CreateSimulationRequest,
    background_tasks: BackgroundTasks
) -> SimulationResponse:
    """Create a new simulation.

    Creates a simulation instance and returns its initial state.
    The simulation does not start automatically; use /simulations/{id}/start to begin.

    Args:
        request: Simulation configuration.
        background_tasks: FastAPI background tasks.

    Returns:
        Initial simulation state.
    """
    # Create agent profile
    agent = AgentProfile(
        name=request.agent_name,
        birth_year=request.birth_year,
        traits=request.traits
    )

    # Create simulation engine with streaming callback
    simulation_id = None
    try:
        # Create engine first to get ID
        engine = SimulationEngine(
            agent=agent,
            starting_location=request.starting_location,
            starting_stress=request.starting_stress,
            inventory=request.inventory
        )
        simulation_id = engine.simulation_id

        # Set up streaming callback
        engine.event_callback = await create_streaming_callback(simulation_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Store simulation
    simulation_engines[simulation_id] = engine
    simulations[simulation_id] = {
        "id": simulation_id,
        "status": engine.status.value,
        "agent_name": agent.name,
        "created_at": datetime.utcnow().isoformat(),
        "engine": engine
    }

    return SimulationResponse(**engine.get_state())


@app.get("/simulations", response_model=List[SimulationListItem])
async def list_simulations() -> List[SimulationListItem]:
    """List all simulations.

    Returns:
        List of simulation summary items.
    """
    items = []
    for sim_data in simulations.values():
        engine = sim_data["engine"]
        state = engine.get_state()
        items.append(SimulationListItem(
            simulation_id=sim_data["id"],
            status=sim_data["status"],
            agent_name=state["agent"]["name"],
            current_location=state["location"]["name"],
            turn=state["turn"],
            created_at=sim_data["created_at"]
        ))

    return items


@app.get("/simulations/{simulation_id}/state", response_model=SimulationResponse)
async def get_simulation_state(simulation_id: str) -> SimulationResponse:
    """Get current state of a simulation.

    Args:
        simulation_id: Simulation ID.

    Returns:
        Current simulation state.

    Raises:
        HTTPException: If simulation not found.
    """
    if simulation_id not in simulation_engines:
        raise HTTPException(status_code=404, detail="Simulation not found")

    engine = simulation_engines[simulation_id]
    return SimulationResponse(**engine.get_state())


@app.post("/simulations/{simulation_id}/start")
async def start_simulation(
    simulation_id: str,
    background_tasks: BackgroundTasks
) -> Dict:
    """Start a simulation running in the background.

    Args:
        simulation_id: Simulation ID.
        background_tasks: FastAPI background tasks.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: If simulation not found or already running.
    """
    if simulation_id not in simulation_engines:
        raise HTTPException(status_code=404, detail="Simulation not found")

    engine = simulation_engines[simulation_id]

    if engine.status == SimulationStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Simulation already running")

    if engine.status == SimulationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Simulation already completed")

    # Run simulation in background
    async def run_simulation():
        try:
            await engine.run()
            simulations[simulation_id]["status"] = engine.status.value
        except Exception as e:
            simulations[simulation_id]["status"] = "failed"
            simulations[simulation_id]["error"] = str(e)

    background_tasks.add_task(run_simulation)

    return {
        "message": "Simulation started",
        "simulation_id": simulation_id,
        "status": "running"
    }


@app.post("/simulations/{simulation_id}/step")
async def step_simulation(simulation_id: str) -> Dict:
    """Execute one step of the simulation.

    Args:
        simulation_id: Simulation ID.

    Returns:
        Step result.

    Raises:
        HTTPException: If simulation not found or completed.
    """
    if simulation_id not in simulation_engines:
        raise HTTPException(status_code=404, detail="Simulation not found")

    engine = simulation_engines[simulation_id]

    if engine.status == SimulationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Simulation already completed")

    if engine.is_safe:
        raise HTTPException(status_code=400, detail="Simulation already reached safety")

    try:
        result = await engine.step()
        simulations[simulation_id]["status"] = engine.status.value
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/simulations/{simulation_id}")
async def delete_simulation(simulation_id: str) -> Dict:
    """Delete a simulation.

    Args:
        simulation_id: Simulation ID.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: If simulation not found.
    """
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    del simulations[simulation_id]
    del simulation_engines[simulation_id]

    return {
        "message": "Simulation deleted",
        "simulation_id": simulation_id
    }


@app.get("/simulations/{simulation_id}/history")
async def get_simulation_history(simulation_id: str) -> Dict:
    """Get the decision history of a simulation.

    Args:
        simulation_id: Simulation ID.

    Returns:
        Decision timeline.

    Raises:
        HTTPException: If simulation not found.
    """
    if simulation_id not in simulation_engines:
        raise HTTPException(status_code=404, detail="Simulation not found")

    engine = simulation_engines[simulation_id]

    history = []
    for frame in engine.history:
        history.append({
            "timestamp": frame.timestamp.isoformat(),
            "action": frame.action,
            "thought_process": frame.thought_process,
            "agent": frame.agent_state.name
        })

    return {
        "simulation_id": simulation_id,
        "total_decisions": len(history),
        "history": history
    }


# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🏛️" * 40)
    print("Historical Mind-Lab API Server Starting...")
    print("🏛️" * 40)
    print(f"\n📊 API Documentation: http://localhost:8000/docs")
    print(f"🔌 WebSocket Endpoint: ws://localhost:8000/ws/simulations/{{id}}")
    print(f"✅ Server ready!\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
