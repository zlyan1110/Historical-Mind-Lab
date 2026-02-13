# 🏛️ Historical Mind-Lab Frontend

Interactive web interface for the Historical Mind-Lab simulation platform, built with Next.js 14, React, and Mapbox GL JS.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Historical Mind-Lab API server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local and add your Mapbox access token
```

### Get a Mapbox Token

1. Sign up at [https://account.mapbox.com/](https://account.mapbox.com/)
2. Go to [Access Tokens](https://account.mapbox.com/access-tokens/)
3. Create a new token or copy your default public token
4. Add it to `.env.local`:
   ```
   NEXT_PUBLIC_MAPBOX_TOKEN=your_token_here
   ```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## ✨ Features

- **🗺️ Interactive Map** - Real-time location tracking with Mapbox GL JS
- **🔌 WebSocket Integration** - Live event streaming from simulations
- **📊 Control Panel** - Create and manage simulations
- **📜 Event Feed** - Real-time display of simulation events
- **📈 Decision History** - View complete decision timeline
- **🎨 Responsive Design** - Works on desktop and mobile

## 🏗️ Project Structure

```
historical-mind-frontend/
├── app/
│   ├── page.tsx           # Main dashboard
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   └── Map.tsx            # Mapbox map component
├── hooks/
│   ├── useSimulation.ts   # REST API hook
│   └── useWebSocket.ts    # WebSocket streaming hook
├── types/
│   └── simulation.ts      # TypeScript type definitions
└── .env.local             # Environment variables (not in git)
```

## 🎮 Usage

### Create a Simulation

1. Enter agent name (default: 颜之推 Yan Zhitui)
2. Select starting location from dropdown
3. Adjust starting stress level (0-100)
4. Click "🆕 Create New Simulation"

### Run the Simulation

After creating a simulation:

- **▶️ Start Simulation** - Run automatically for N turns
- **⏭️ Step** - Execute one turn at a time
- **📜 View History** - Display complete decision timeline

### Watch Real-Time Events

The event feed shows live updates via WebSocket:

- 🔌 Connection established
- 🚀 Simulation started
- 🔄 Turn start
- 📜 Historical events
- 🤔 Agent thinking process
- 💭 Agent decisions
- ⚡ Actions executed
- 📊 State updates
- ✅ Simulation completed

### Monitor the Map

The interactive map displays:

- Current agent location (red marker)
- Location name and coordinates
- Smooth animations when moving
- Zoom and pan controls

## 🛠️ Development

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint
```

### API Endpoints Used

- `POST /simulations` - Create new simulation
- `GET /simulations/{id}/state` - Get current state
- `POST /simulations/{id}/start` - Start simulation
- `POST /simulations/{id}/step` - Execute one step
- `GET /simulations/{id}/history` - Get decision history
- `WS /ws/simulations/{id}` - WebSocket event stream

## 📝 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Mapbox access token | Required |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |

### Customization

**Change Map Style:**
Edit `components/Map.tsx`:
```typescript
style: 'mapbox://styles/mapbox/streets-v12'
// Available: streets-v12, outdoors-v12, light-v11, dark-v11, satellite-v9
```

**Add New Locations:**
Edit `app/page.tsx` in the location select dropdown:
```typescript
<option value="新地点">新地点 (New Place)</option>
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Add environment variables in Vercel dashboard
```

### Docker

```bash
# Build image
docker build -t historical-mind-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_MAPBOX_TOKEN=your_token \
  historical-mind-frontend
```

## 🐛 Troubleshooting

**Map not loading?**
- Check your Mapbox token in `.env.local`
- Verify the token is valid at [mapbox.com/account](https://account.mapbox.com/)

**WebSocket not connecting?**
- Ensure the API server is running on `http://localhost:8000`
- Check browser console for connection errors
- Verify CORS is enabled on the backend

**API calls failing?**
- Start the backend: `cd ../.. && ./start_server.sh`
- Check API health: `curl http://localhost:8000/health`

## 📚 Documentation

- [Historical Mind-Lab API](../../API.md)
- [Frontend Guide](../../FRONTEND_GUIDE.md)
- [Project Overview](../../README.md)

## 🔗 Links

- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Next.js Docs:** [nextjs.org/docs](https://nextjs.org/docs)
- **Mapbox GL JS:** [docs.mapbox.com/mapbox-gl-js](https://docs.mapbox.com/mapbox-gl-js)

---

**Built with Next.js 14, React, TypeScript, Tailwind CSS, and Mapbox GL JS** 🚀
