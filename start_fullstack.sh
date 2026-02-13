#!/bin/bash

# Historical Mind-Lab Full Stack Startup Script
# Starts both backend API and frontend Next.js app

echo "🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️"
echo "Historical Mind-Lab - Full Stack Startup"
echo "🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️"
echo ""

# Check if backend is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API already running on http://localhost:8000"
else
    echo "🚀 Starting Backend API Server..."
    PYTHONPATH=$(pwd) uvicorn src.api.server:app --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
    sleep 2

    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API started successfully"
    else
        echo "❌ Backend API failed to start. Check backend.log"
        exit 1
    fi
fi

echo ""

# Check if frontend is already running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend already running on http://localhost:3000"
else
    echo "🚀 Starting Frontend Next.js Server..."
    cd historical-mind-frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo "   Frontend PID: $FRONTEND_PID"
    sleep 3

    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend started successfully"
    else
        echo "❌ Frontend failed to start. Check frontend.log"
        exit 1
    fi
fi

echo ""
echo "🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️"
echo "✨ Historical Mind-Lab is Ready! ✨"
echo "🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️🏛️"
echo ""
echo "📡 Backend API:      http://localhost:8000"
echo "📚 API Docs:         http://localhost:8000/docs"
echo "🌐 Frontend App:     http://localhost:3000"
echo ""
echo "🛑 To stop servers:  pkill -f uvicorn && pkill -f 'next dev'"
echo "📊 View logs:        tail -f backend.log frontend.log"
echo ""
echo "Happy simulating! 🏛️"
