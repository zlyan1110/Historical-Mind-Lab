# 🚀 Historical Mind-Lab - Quick Start Guide

Complete guide to running the full-stack Historical Mind-Lab application.

---

## 📋 Prerequisites

- ✅ Python 3.12+
- ✅ Node.js 18+
- ✅ Mapbox access token (free at [mapbox.com](https://account.mapbox.com/))

---

## ⚡ One-Command Startup

```bash
./start_fullstack.sh
```

This starts both:
- 🔧 **Backend API** on http://localhost:8000
- 🌐 **Frontend App** on http://localhost:3000

---

## 🎯 Step-by-Step Usage

### 1. Start the Application

**Option A: Full Stack (Recommended)**
```bash
./start_fullstack.sh
```

**Option B: Separate Servers**
```bash
# Terminal 1 - Backend
./start_server.sh

# Terminal 2 - Frontend
cd historical-mind-frontend
npm run dev
```

### 2. Open Your Browser

Visit **http://localhost:3000**

You should see:
- 🏛️ Header: "Historical Mind-Lab"
- 📋 Left panel: Simulation controls
- 🗺️ Right panel: Interactive map (with your Mapbox token!)

### 3. Create Your First Simulation

**In the "Create Simulation" panel:**

1. **Agent Name:** Keep default `颜之推 (Yan Zhitui)` or customize
2. **Starting Location:** Choose from dropdown
   - 建康 (Jiankang) - Default, high danger
   - 江陵 (Jiangling) - Safe haven
   - 襄阳 (Xiangyang)
   - 寿阳 (Shouyang)
3. **Starting Stress:** Drag slider (0-100)
   - 0-49: Analytical mode
   - 50-79: Tactical mode
   - 80-100: Survival mode
4. Click **"🆕 Create New Simulation"**

**What happens:**
- Simulation created with unique ID
- WebSocket connects (🟢 Connected)
- Map shows starting location
- "Simulation Controls" panel appears

### 4. Run the Simulation

**You have three options:**

**A. Auto-Run (Recommended for first try)**
1. Set "Max Turns" slider (default: 10)
2. Click **"▶️ Start Simulation"**
3. Watch events stream in real-time!

**B. Step-by-Step**
1. Click **"⏭️ Step (1 Turn)"**
2. Watch one decision at a time
3. Repeat for full control

**C. View History**
1. Click **"📜 View History"**
2. See complete decision timeline
3. Review agent's thought process

### 5. Watch the Magic Happen

**Real-Time Event Feed:**
- 🔌 `connection_established` - WebSocket connected
- 🚀 `simulation_started` - Simulation begins
- 🔄 `turn_start` - New turn begins
- 📜 `historical_event` - Historical event triggered
- 🤔 `agent_thinking` - Agent processes information
- 💭 `agent_decision` - Decision made
- ⚡ `action_executed` - Action completed
- 📊 `state_update` - State updated
- ✅ `simulation_completed` - Simulation ends

**Interactive Map:**
- Red marker shows current location
- Smooth animations when moving
- Click marker for location details
- Pan/zoom with mouse or controls

**Current State Panel:**
- Turn number
- Current location
- Stress level (color-coded)
- Focus (e.g., "Family Safety")
- Status badge (running/completed)

---

## 📊 Example Simulation Run

```
Initial Setup:
Agent: 颜之推 (Yan Zhitui)
Location: 建康 (Jiankang)
Stress: 40
Danger: 90/100 (city under siege)

Turn 1:
Event: 台城失守 (Palace falls)
Thought: "Fire approaching. Jiangling safer under Xiao Yi's control."
Decision: move_to:江陵
Action: Travel 654.9 km by boat (4.4 days)
Result: ✅ Reached safe haven!
Stress: 40 → 25

Turn 2:
Location: 江陵 (Jiangling)
Danger: 30/100 (relatively safe)
Stress: 25
Event: None (calm period)
Decision: gather_information
```

---

## 🎮 Interactive Features

### Control Panel
- **Create** multiple simulations
- **Switch** between simulations
- **Adjust** parameters on the fly
- **Monitor** WebSocket status

### Event Stream
- **Real-time** updates (<5ms latency)
- **Detailed** JSON data for each event
- **Timestamp** for every event
- **Auto-scroll** to latest event

### Map View
- **Interactive** markers
- **Smooth** animations
- **Popup** details on click
- **Navigation** controls

### Decision History
- **Complete** timeline
- **Turn-by-turn** breakdown
- **Thought process** visible
- **Stress tracking** over time

---

## 🐛 Troubleshooting

### Map Not Loading?

**Problem:** Map shows "Loading map..." forever

**Solutions:**
1. Check `.env.local` has valid `NEXT_PUBLIC_MAPBOX_TOKEN`
2. Verify token at https://account.mapbox.com/access-tokens/
3. Restart frontend: `pkill -f 'next dev' && cd historical-mind-frontend && npm run dev`

### WebSocket Not Connecting?

**Problem:** Shows "🔴 Disconnected"

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check browser console for errors (F12)
3. Ensure CORS is enabled in backend (already configured)

### API Calls Failing?

**Problem:** Error messages when creating simulation

**Solutions:**
1. Check backend health: `curl http://localhost:8000/health`
2. View backend logs: `tail -f server.log` or `tail -f backend.log`
3. Restart backend: `./start_server.sh`

### Port Already in Use?

**Problem:** "Port 3000 already in use"

**Solutions:**
```bash
# Kill existing frontend
pkill -f 'next dev'

# Or use different port
cd historical-mind-frontend
PORT=3001 npm run dev
```

---

## 📚 API Endpoints (for developers)

### REST API (http://localhost:8000)

```bash
# Health check
curl http://localhost:8000/health

# Create simulation
curl -X POST http://localhost:8000/simulations \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"颜之推","starting_location":"建康"}'

# Get state
curl http://localhost:8000/simulations/{id}/state

# Start simulation
curl -X POST http://localhost:8000/simulations/{id}/start \
  -H "Content-Type: application/json" \
  -d '{"max_turns":10}'

# View history
curl http://localhost:8000/simulations/{id}/history
```

### WebSocket (ws://localhost:8000)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/simulations/{id}');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.data);
};
```

---

## 🛑 Stopping the Application

**Stop all servers:**
```bash
pkill -f uvicorn && pkill -f 'next dev'
```

**Stop individually:**
```bash
# Backend only
pkill -f uvicorn

# Frontend only
pkill -f 'next dev'
```

---

## 📖 Next Steps

### Explore More Features
- Try different starting locations
- Adjust stress levels and observe behavior changes
- Run multiple simulations in parallel
- Analyze decision patterns in history view

### Customize Your Experience
- **Map Style:** Edit `historical-mind-frontend/components/Map.tsx`
- **Add Locations:** Edit `src/tools/gis.py` (backend)
- **New Events:** Edit `data/history_facts.json`

### Deploy to Production
- **Frontend:** Deploy to Vercel (see `historical-mind-frontend/README.md`)
- **Backend:** Containerize with Docker (see main `README.md`)

### Advanced Usage
- **Real LLM Integration:** Replace mock with PydanticAI + Claude API
- **Multi-Agent Scenarios:** Simulate multiple historical figures
- **Analytics Dashboard:** Track patterns across simulations

---

## 📞 Getting Help

- **API Documentation:** http://localhost:8000/docs
- **Frontend README:** `historical-mind-frontend/README.md`
- **Backend README:** `README.md`
- **Architecture:** `PHASE3_SUMMARY.md`
- **Full Guide:** `PROJECT_COMPLETE.md`

---

## 🎉 You're Ready!

The Historical Mind-Lab platform is now fully operational. Simulate history, make decisions, survive chaos!

**Happy Simulating! 🏛️**
