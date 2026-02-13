# 🎨 Frontend Development Guide

## Overview

This guide walks you through building a web interface for Historical Mind-Lab using **Next.js 14**, **React**, and **Mapbox GL JS** to visualize historical simulations in real-time.

---

## 🎯 What We'll Build

A single-page application with:
- **Interactive Map** - Mapbox GL JS showing ancient Chinese locations
- **Real-Time Updates** - WebSocket streaming of simulation events
- **Control Panel** - Create and manage simulations
- **Decision Timeline** - Visual history of agent decisions
- **Status Dashboard** - Current location, stress level, inventory

---

## 🚀 Quick Start

### 1. Create Next.js App

```bash
# Navigate to your projects folder
cd ~/projects

# Create Next.js app
npx create-next-app@latest historical-mind-frontend

# During setup, choose:
✔ TypeScript? Yes
✔ ESLint? Yes
✔ Tailwind CSS? Yes
✔ `src/` directory? Yes
✔ App Router? Yes
✔ Import alias? Yes (@/*)

cd historical-mind-frontend
```

### 2. Install Dependencies

```bash
npm install mapbox-gl
npm install --save-dev @types/mapbox-gl

# For API calls
npm install axios

# For WebSocket (built-in, but types help)
npm install --save-dev @types/ws
```

### 3. Get Mapbox Access Token

1. Go to https://www.mapbox.com/
2. Sign up (free tier is sufficient)
3. Get your access token from https://account.mapbox.com/access-tokens/

### 4. Configure Environment

Create `.env.local`:

```bash
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 📁 Project Structure

```
historical-mind-frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main page
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── components/
│   │   ├── Map.tsx               # Mapbox map component
│   │   ├── ControlPanel.tsx     # Simulation controls
│   │   ├── Timeline.tsx          # Decision history
│   │   ├── StatusDashboard.tsx   # Current state display
│   │   └── EventFeed.tsx         # Real-time event log
│   ├── hooks/
│   │   ├── useSimulation.ts      # Simulation API hook
│   │   └── useWebSocket.ts       # WebSocket hook
│   └── types/
│       └── simulation.ts         # TypeScript types
└── public/
    └── markers/                  # Custom map markers
```

---

## 🗺️ Step 1: Create Map Component

**`src/components/Map.tsx`**

```typescript
'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface MapProps {
  currentLocation?: {
    lat: number;
    lon: number;
    name: string;
  };
  onMapClick?: (lat: number, lon: number) => void;
}

export default function Map({ currentLocation, onMapClick }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const marker = useRef<mapboxgl.Marker | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current) return;

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN!;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [118.7966, 32.0583], // Jiankang (Nanjing)
      zoom: 6,
      projection: 'globe' as any
    });

    map.current.on('load', () => {
      setMapLoaded(true);

      // Add historical locations layer
      map.current!.addSource('locations', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: { type: 'Point', coordinates: [118.7966, 32.0583] },
              properties: { name: '建康 (Jiankang)', danger: 90 }
            },
            {
              type: 'Feature',
              geometry: { type: 'Point', coordinates: [112.2051, 30.3509] },
              properties: { name: '江陵 (Jiangling)', danger: 20 }
            },
            {
              type: 'Feature',
              geometry: { type: 'Point', coordinates: [116.0006, 29.7272] },
              properties: { name: '寻阳 (Xunyang)', danger: 40 }
            }
          ]
        }
      });

      map.current!.addLayer({
        id: 'locations',
        type: 'circle',
        source: 'locations',
        paint: {
          'circle-radius': 8,
          'circle-color': [
            'case',
            ['<', ['get', 'danger'], 30], '#22c55e', // Green (safe)
            ['<', ['get', 'danger'], 70], '#eab308', // Yellow (moderate)
            '#ef4444' // Red (dangerous)
          ],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff'
        }
      });

      // Add labels
      map.current!.addLayer({
        id: 'location-labels',
        type: 'symbol',
        source: 'locations',
        layout: {
          'text-field': ['get', 'name'],
          'text-size': 12,
          'text-offset': [0, 1.5],
          'text-anchor': 'top'
        },
        paint: {
          'text-color': '#000',
          'text-halo-color': '#fff',
          'text-halo-width': 2
        }
      });
    });

    // Handle click events
    if (onMapClick) {
      map.current.on('click', (e) => {
        onMapClick(e.lngLat.lat, e.lngLat.lng);
      });
    }

    return () => {
      map.current?.remove();
    };
  }, [onMapClick]);

  // Update current location marker
  useEffect(() => {
    if (!map.current || !mapLoaded || !currentLocation) return;

    // Remove old marker
    if (marker.current) {
      marker.current.remove();
    }

    // Add new marker
    const el = document.createElement('div');
    el.className = 'custom-marker';
    el.style.width = '30px';
    el.style.height = '30px';
    el.style.backgroundImage = 'url(/markers/agent.png)';
    el.style.backgroundSize = 'contain';
    el.innerHTML = '🧍'; // Agent emoji as fallback
    el.style.fontSize = '30px';

    marker.current = new mapboxgl.Marker(el)
      .setLngLat([currentLocation.lon, currentLocation.lat])
      .setPopup(
        new mapboxgl.Popup().setHTML(
          `<strong>${currentLocation.name}</strong>`
        )
      )
      .addTo(map.current);

    // Fly to location
    map.current.flyTo({
      center: [currentLocation.lon, currentLocation.lat],
      zoom: 8,
      duration: 2000
    });
  }, [currentLocation, mapLoaded]);

  return (
    <div
      ref={mapContainer}
      className="w-full h-full rounded-lg shadow-lg"
    />
  );
}
```

---

## 🔌 Step 2: Create WebSocket Hook

**`src/hooks/useWebSocket.ts`**

```typescript
import { useEffect, useRef, useState } from 'react';

interface SimulationEvent {
  type: string;
  data: any;
  timestamp: string;
}

export function useWebSocket(simulationId: string | null) {
  const [events, setEvents] = useState<SimulationEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [latestEvent, setLatestEvent] = useState<SimulationEvent | null>(null);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!simulationId) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/simulations/${simulationId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      const data: SimulationEvent = JSON.parse(event.data);
      console.log('Event received:', data.type, data.data);

      setEvents((prev) => [...prev, data]);
      setLatestEvent(data);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, [simulationId]);

  return { events, isConnected, latestEvent };
}
```

---

## 🎮 Step 3: Create Simulation API Hook

**`src/hooks/useSimulation.ts`**

```typescript
import axios from 'axios';
import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface SimulationState {
  simulation_id: string;
  status: string;
  turn: number;
  location: {
    name: string;
    lat: number;
    lon: number;
    danger_level: number;
  };
  psychology: {
    stress: number;
    focus: string;
    mbti: string;
  };
  inventory: string[];
}

export function useSimulation() {
  const [simulation, setSimulation] = useState<SimulationState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createSimulation = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/simulations`, {
        agent_name: '颜之推 (Yan Zhitui)',
        starting_location: '建康',
        starting_stress: 40
      });

      setSimulation(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const startSimulation = async (id: string) => {
    try {
      await axios.post(`${API_URL}/simulations/${id}/start`);
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const getState = async (id: string) => {
    try {
      const response = await axios.get(`${API_URL}/simulations/${id}/state`);
      setSimulation(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  return {
    simulation,
    loading,
    error,
    createSimulation,
    startSimulation,
    getState
  };
}
```

---

## 📊 Step 4: Create Main Page

**`src/app/page.tsx`**

```typescript
'use client';

import { useState, useEffect } from 'react';
import Map from '@/components/Map';
import { useSimulation } from '@/hooks/useSimulation';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function Home() {
  const { simulation, createSimulation, startSimulation } = useSimulation();
  const { events, isConnected, latestEvent } = useWebSocket(simulation?.simulation_id || null);
  const [currentLocation, setCurrentLocation] = useState<any>(null);

  // Update location when state changes
  useEffect(() => {
    if (simulation) {
      setCurrentLocation(simulation.location);
    }
  }, [simulation]);

  // Update location from WebSocket events
  useEffect(() => {
    if (latestEvent?.type === 'state_update') {
      setCurrentLocation(latestEvent.data.location);
    }
  }, [latestEvent]);

  const handleCreateAndStart = async () => {
    const newSim = await createSimulation();
    await startSimulation(newSim.simulation_id);
  };

  return (
    <main className="h-screen flex">
      {/* Left Panel */}
      <div className="w-96 bg-gray-900 text-white p-6 overflow-y-auto">
        <h1 className="text-2xl font-bold mb-6">🏛️ Historical Mind-Lab</h1>

        {/* Control Panel */}
        <div className="mb-6">
          <button
            onClick={handleCreateAndStart}
            className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium"
          >
            Start New Simulation
          </button>
        </div>

        {/* Status Dashboard */}
        {simulation && (
          <div className="mb-6 bg-gray-800 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-3">Status</h2>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-400">Location:</span>
                <span className="ml-2">{simulation.location.name}</span>
              </div>
              <div>
                <span className="text-gray-400">Danger:</span>
                <span className="ml-2">{simulation.location.danger_level}/100</span>
              </div>
              <div>
                <span className="text-gray-400">Stress:</span>
                <span className="ml-2">{simulation.psychology.stress}/100</span>
              </div>
              <div>
                <span className="text-gray-400">Turn:</span>
                <span className="ml-2">{simulation.turn}</span>
              </div>
              <div>
                <span className="text-gray-400">Connection:</span>
                <span className={`ml-2 ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                  {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Event Feed */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-3">Event Log</h2>
          <div className="space-y-2 text-sm max-h-96 overflow-y-auto">
            {events.slice().reverse().map((event, i) => (
              <div key={i} className="border-l-2 border-blue-500 pl-3 py-1">
                <div className="font-medium text-blue-400">{event.type}</div>
                <div className="text-gray-400 text-xs">
                  {JSON.stringify(event.data).substring(0, 100)}...
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 p-4 bg-gray-100">
        <Map currentLocation={currentLocation} />
      </div>
    </main>
  );
}
```

---

## 🎨 Step 5: Add Global Styles

**`src/app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.custom-marker {
  cursor: pointer;
}

/* Mapbox overrides */
.mapboxgl-popup-content {
  padding: 10px 15px;
  border-radius: 8px;
  font-family: inherit;
}
```

---

## 🚀 Running the Frontend

### 1. Start the Backend

```bash
cd Historical-Mind-Lab
./start_server.sh
```

### 2. Start the Frontend

```bash
cd historical-mind-frontend
npm run dev
```

### 3. Open in Browser

```
http://localhost:3000
```

---

## 🎯 What You'll See

1. **Map View** - Interactive Mapbox map centered on ancient China
2. **Control Panel** - Button to create and start simulations
3. **Status Dashboard** - Real-time location, stress, danger levels
4. **Event Feed** - Live WebSocket events streaming in
5. **Agent Marker** - Animated marker moving on the map

---

## 🔧 Advanced Features

### Add Route Visualization

```typescript
// In Map component, add route line
map.current!.addSource('route', {
  type: 'geojson',
  data: {
    type: 'Feature',
    geometry: {
      type: 'LineString',
      coordinates: [
        [118.7966, 32.0583], // Jiankang
        [112.2051, 30.3509]  // Jiangling
      ]
    }
  }
});

map.current!.addLayer({
  id: 'route',
  type: 'line',
  source: 'route',
  paint: {
    'line-color': '#3b82f6',
    'line-width': 3,
    'line-dasharray': [2, 2]
  }
});
```

### Add Decision Timeline

```typescript
const Timeline = ({ events }: { events: SimulationEvent[] }) => {
  const decisions = events.filter(e => e.type === 'agent_decision');

  return (
    <div className="space-y-3">
      {decisions.map((event, i) => (
        <div key={i} className="flex items-start">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs">
            {i + 1}
          </div>
          <div className="ml-3">
            <div className="font-medium">{event.data.action}</div>
            <div className="text-sm text-gray-400">{event.data.reasoning}</div>
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

## 📦 Deployment

### Deploy Backend (Railway/Render)

```bash
# Add Procfile
echo "web: uvicorn src.api.server:app --host 0.0.0.0 --port $PORT" > Procfile

# Push to Railway/Render
git push railway main
```

### Deploy Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Update environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app
```

---

## 🎓 Next Steps

- Add authentication (NextAuth.js)
- Persist simulation history (PostgreSQL)
- Add charts for stress/danger over time
- Multi-agent view (split screen)
- Mobile responsive design
- Dark/light mode toggle

---

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

**🏛️ Build your historical simulation interface!** 🏛️
