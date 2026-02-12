"""WebSocket handler for real-time simulation streaming.

This module provides WebSocket endpoints for streaming simulation events
in real-time to connected clients.
"""

import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

from src.domain.schemas import AgentProfile
from src.simulation.engine import SimulationEngine, SimulationEvent

# WebSocket router
router = APIRouter()

# Active WebSocket connections per simulation
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for simulation streaming."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, simulation_id: str):
        """Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection.
            simulation_id: ID of simulation to stream.
        """
        await websocket.accept()
        if simulation_id not in self.active_connections:
            self.active_connections[simulation_id] = set()
        self.active_connections[simulation_id].add(websocket)

    def disconnect(self, websocket: WebSocket, simulation_id: str):
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection.
            simulation_id: ID of simulation.
        """
        if simulation_id in self.active_connections:
            self.active_connections[simulation_id].discard(websocket)
            if not self.active_connections[simulation_id]:
                del self.active_connections[simulation_id]

    async def send_event(self, event: SimulationEvent, simulation_id: str):
        """Broadcast an event to all connected clients.

        Args:
            event: Simulation event to send.
            simulation_id: ID of simulation.
        """
        if simulation_id not in self.active_connections:
            return

        # Convert event to JSON
        message = json.dumps(event.to_dict())

        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections[simulation_id]:
            try:
                await connection.send_text(message)
            except Exception:
                # Mark for removal if send fails
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, simulation_id)

    async def send_json(self, data: Dict, simulation_id: str):
        """Send JSON data to all connected clients.

        Args:
            data: Data dictionary to send.
            simulation_id: ID of simulation.
        """
        if simulation_id not in self.active_connections:
            return

        message = json.dumps(data)

        disconnected = set()
        for connection in self.active_connections[simulation_id]:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection, simulation_id)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/simulations/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str):
    """WebSocket endpoint for streaming simulation events.

    Args:
        websocket: WebSocket connection.
        simulation_id: ID of simulation to stream.
    """
    await manager.connect(websocket, simulation_id)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "simulation_id": simulation_id,
                "message": "Connected to simulation stream"
            }
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (ping/pong, commands, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle client commands
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "data": {"timestamp": message.get("timestamp")}
                    })

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"}
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": str(e)}
                })
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, simulation_id)


async def create_streaming_callback(simulation_id: str):
    """Create an event callback for streaming simulation events.

    Args:
        simulation_id: ID of simulation.

    Returns:
        Async callback function.
    """
    async def callback(event: SimulationEvent):
        """Send event to all connected WebSocket clients.

        Args:
            event: Simulation event.
        """
        await manager.send_event(event, simulation_id)

    return callback


# Helper function to be used by simulation engine
async def stream_simulation_events(engine: SimulationEngine):
    """Stream all events from a simulation engine via WebSocket.

    Args:
        engine: Simulation engine to stream.
    """
    callback = await create_streaming_callback(engine.simulation_id)
    engine.event_callback = callback
