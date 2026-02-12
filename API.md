# 🌐 Historical Mind-Lab API Documentation

## Overview

The Historical Mind-Lab API provides REST and WebSocket interfaces for creating and managing historical agent simulations. It enables real-time streaming of agent decisions, thoughts, and actions.

**Base URL:** `http://localhost:8000`
**WebSocket URL:** `ws://localhost:8000`

---

## 🚀 Quick Start

### 1. Start the Server

```bash
./start_server.sh
```

Or:

```bash
PYTHONPATH=$(pwd) uvicorn src.api.server:app --reload
```

### 2. Access API Documentation

- **Interactive Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 3. Run Test Client

```bash
python3 test_api.py
```

---

## 📡 REST API Endpoints

### Health Check

**GET** `/health`

Check API server health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-12T10:30:00.000Z",
  "active_simulations": 2
}
```

---

### Create Simulation

**POST** `/simulations`

Create a new simulation instance.

**Request Body:**
```json
{
  "agent_name": "颜之推 (Yan Zhitui)",
  "birth_year": 531,
  "traits": ["Analytical", "Pragmatic", "Observant"],
  "starting_location": "建康",
  "starting_stress": 40,
  "inventory": ["经书三卷", "银两若干", "家书"]
}
```

**Response (201 Created):**
```json
{
  "simulation_id": "a1b2c3d4-...",
  "status": "created",
  "turn": 0,
  "agent": {
    "name": "颜之推 (Yan Zhitui)",
    "birth_year": 531,
    "traits": ["Analytical", "Pragmatic", "Observant"]
  },
  "location": {
    "name": "建康",
    "lat": 32.0583,
    "lon": 118.7966,
    "danger_level": 90
  },
  "psychology": {
    "stress": 40,
    "focus": "Family Safety",
    "mbti": "ISTP"
  },
  "inventory": ["经书三卷", "银两若干", "家书"],
  "current_time": "0548-12-15T14:00:00",
  "is_safe": false,
  "decisions_made": 0
}
```

---

### List Simulations

**GET** `/simulations`

Get a list of all simulations.

**Response:**
```json
[
  {
    "simulation_id": "a1b2c3d4-...",
    "status": "running",
    "agent_name": "颜之推 (Yan Zhitui)",
    "current_location": "建康",
    "turn": 1,
    "created_at": "2026-02-12T10:30:00.000Z"
  }
]
```

---

### Get Simulation State

**GET** `/simulations/{simulation_id}/state`

Get the current state of a simulation.

**Response:**
```json
{
  "simulation_id": "a1b2c3d4-...",
  "status": "running",
  "turn": 1,
  "agent": { ... },
  "location": {
    "name": "江陵",
    "lat": 30.3509,
    "lon": 112.2051,
    "danger_level": 20
  },
  "psychology": {
    "stress": 70,
    "focus": "Family Safety",
    "mbti": "ISTP"
  },
  "current_time": "0548-12-19T22:00:00",
  "is_safe": true,
  "decisions_made": 1
}
```

---

### Start Simulation

**POST** `/simulations/{simulation_id}/start`

Start a simulation running in the background.

**Response:**
```json
{
  "message": "Simulation started",
  "simulation_id": "a1b2c3d4-...",
  "status": "running"
}
```

---

### Execute Step

**POST** `/simulations/{simulation_id}/step`

Execute one step of the simulation manually.

**Response:**
```json
{
  "turn": 1,
  "event": "【台城失守】台城(皇宫)失守...",
  "decision": {
    "reasoning": "台城已陷，火光逼近...",
    "next_action": "move_to:江陵"
  },
  "action_result": {
    "action": "move_to:江陵",
    "success": true,
    "route": {
      "distance_km": 654.9,
      "direction": "西南偏西",
      "travel_time_hours": 107
    },
    "reached_safety": true
  },
  "state": { ... }
}
```

---

### Get Decision History

**GET** `/simulations/{simulation_id}/history`

Get the complete decision timeline.

**Response:**
```json
{
  "simulation_id": "a1b2c3d4-...",
  "total_decisions": 1,
  "history": [
    {
      "timestamp": "0548-12-15T14:00:00",
      "action": "move_to:江陵",
      "thought_process": "台城已陷，火光逼近。根据历史情报...",
      "agent": "颜之推 (Yan Zhitui)"
    }
  ]
}
```

---

### Delete Simulation

**DELETE** `/simulations/{simulation_id}`

Delete a simulation instance.

**Response:**
```json
{
  "message": "Simulation deleted",
  "simulation_id": "a1b2c3d4-..."
}
```

---

## 🔌 WebSocket Streaming

### Connect to Stream

**WS** `/ws/simulations/{simulation_id}`

Connect to real-time event stream for a simulation.

### Connection Flow

1. **Connect:**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/simulations/{id}');
   ```

2. **Receive connection confirmation:**
   ```json
   {
     "type": "connection_established",
     "data": {
       "simulation_id": "a1b2c3d4-...",
       "message": "Connected to simulation stream"
     },
     "timestamp": "2026-02-12T10:30:00.000Z"
   }
   ```

3. **Start simulation via REST API:**
   ```bash
   POST /simulations/{id}/start
   ```

4. **Receive real-time events**

### Event Types

#### `simulation_started`
```json
{
  "type": "simulation_started",
  "data": {
    "turn": 0,
    "location": { ... },
    "stress": 40
  }
}
```

#### `turn_start`
```json
{
  "type": "turn_start",
  "data": {
    "turn": 1,
    "state": { ... }
  }
}
```

#### `historical_event`
```json
{
  "type": "historical_event",
  "data": {
    "description": "【台城失守】台城(皇宫)失守...",
    "threat_level": 95
  }
}
```

#### `agent_thinking`
```json
{
  "type": "agent_thinking",
  "data": {
    "stress": 100,
    "location": "建康"
  }
}
```

#### `agent_decision`
```json
{
  "type": "agent_decision",
  "data": {
    "reasoning": "台城已陷，火光逼近。根据历史情报...",
    "action": "move_to:江陵"
  }
}
```

#### `action_executed`
```json
{
  "type": "action_executed",
  "data": {
    "action": "move_to:江陵",
    "success": true,
    "route": {
      "distance_km": 654.9,
      "direction": "西南偏西",
      "travel_time_hours": 107
    },
    "reached_safety": true,
    "old_location": "建康",
    "new_location": "江陵"
  }
}
```

#### `state_update`
```json
{
  "type": "state_update",
  "data": {
    "simulation_id": "a1b2c3d4-...",
    "status": "running",
    "turn": 1,
    "location": { ... },
    "psychology": { ... }
  }
}
```

#### `simulation_completed`
```json
{
  "type": "simulation_completed",
  "data": {
    "simulation_id": "a1b2c3d4-...",
    "status": "completed",
    "location": { "name": "江陵" },
    "psychology": { "stress": 70 },
    "is_safe": true
  }
}
```

#### `simulation_error`
```json
{
  "type": "simulation_error",
  "data": {
    "error": "Error message",
    "turn": 1
  }
}
```

---

## 💻 Client Examples

### Python with httpx

```python
import asyncio
import httpx

async def create_simulation():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/simulations",
            json={
                "agent_name": "颜之推 (Yan Zhitui)",
                "starting_location": "建康",
                "starting_stress": 40
            }
        )
        return response.json()

simulation = asyncio.run(create_simulation())
print(f"Created: {simulation['simulation_id']}")
```

### Python with websockets

```python
import asyncio
import websockets
import json

async def stream_simulation(simulation_id):
    uri = f"ws://localhost:8000/ws/simulations/{simulation_id}"

    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            event = json.loads(message)
            print(f"{event['type']}: {event['data']}")

asyncio.run(stream_simulation("a1b2c3d4-..."))
```

### JavaScript (Browser)

```javascript
// Create simulation
fetch('http://localhost:8000/simulations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    agent_name: '颜之推 (Yan Zhitui)',
    starting_location: '建康',
    starting_stress: 40
  })
})
.then(res => res.json())
.then(sim => {
  console.log('Created:', sim.simulation_id);

  // Connect WebSocket
  const ws = new WebSocket(`ws://localhost:8000/ws/simulations/${sim.simulation_id}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.type, data.data);
  };

  // Start simulation
  fetch(`http://localhost:8000/simulations/${sim.simulation_id}/start`, {
    method: 'POST'
  });
});
```

### cURL

```bash
# Create simulation
curl -X POST http://localhost:8000/simulations \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"颜之推","starting_location":"建康","starting_stress":40}'

# Get state
curl http://localhost:8000/simulations/{id}/state

# Start simulation
curl -X POST http://localhost:8000/simulations/{id}/start

# Get history
curl http://localhost:8000/simulations/{id}/history
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTP REST
       ├──────────────────┐
       │                  │
       │                  │ WebSocket
┌──────▼──────┐    ┌──────▼──────┐
│  FastAPI    │    │  WebSocket  │
│   Server    │◄───┤   Handler   │
└──────┬──────┘    └──────┬──────┘
       │                  │
       │                  │
┌──────▼──────────────────▼──────┐
│     Simulation Engine          │
│  (Event-driven architecture)   │
└──────┬─────────────────────────┘
       │
       ├─────┬─────┬──────┐
       │     │     │      │
┌──────▼─┐ ┌─▼───┐ ┌▼────▼───┐
│ Domain │ │Tools│ │ Agents  │
│Schemas │ │(GIS)│ │(Prompts)│
└────────┘ └─────┘ └─────────┘
```

---

## 📊 Status Codes

- **200 OK:** Request successful
- **201 Created:** Resource created successfully
- **400 Bad Request:** Invalid request parameters
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

---

## 🔒 Security Notes

**For MVP/Development:**
- CORS is set to allow all origins (`*`)
- No authentication required
- Data stored in-memory (lost on restart)

**For Production:**
- Implement authentication (JWT, API keys)
- Restrict CORS to specific origins
- Use persistent storage (Redis, PostgreSQL)
- Add rate limiting
- Enable HTTPS/WSS

---

## 🎯 Next Steps

1. **Frontend Integration:** Build React/Next.js UI
2. **Real LLM:** Replace mock with PydanticAI
3. **Persistent Storage:** Add database layer
4. **Authentication:** Add user accounts
5. **Multi-Agent:** Support multiple concurrent agents

---

## 📝 Files

- `src/api/server.py` - FastAPI REST server
- `src/api/websocket.py` - WebSocket streaming
- `src/simulation/engine.py` - Core simulation engine
- `test_api.py` - Test client
- `start_server.sh` - Server startup script

---

**Documentation Version:** 1.0.0
**Last Updated:** 2026-02-12
