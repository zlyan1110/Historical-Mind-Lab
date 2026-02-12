#!/bin/bash
# Start Historical Mind-Lab API server

cd "$(dirname "$0")"

echo "🏛️  Starting Historical Mind-Lab API Server..."
echo ""
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔌 WebSocket: ws://localhost:8000/ws/simulations/{id}"
echo ""

PYTHONPATH=$(pwd) uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
