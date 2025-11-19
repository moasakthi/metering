#!/bin/bash
# Quick start script for local development

set -e

echo "🚀 Starting Metering Framework (Local Development)"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python 3 found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi
echo "✅ Node.js found"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found in PATH (may still work if running)"
else
    echo "✅ PostgreSQL found"
fi

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis not found in PATH (may still work if running)"
else
    echo "✅ Redis found"
    # Test Redis connection
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running. Start it with: redis-server"
    fi
fi

echo ""
echo -e "${GREEN}Starting services...${NC}"
echo ""

# Start API in background
echo "📡 Starting API service..."
cd services/api

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing API dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    touch .deps_installed
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your database credentials"
fi

# Start API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "✅ API started (PID: $API_PID)"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"

cd ../..

# Start UI in background
echo ""
echo "🎨 Starting UI service..."
cd services/ui

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing UI dependencies..."
    npm install > /dev/null 2>&1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
    fi
fi

# Start UI
npm run dev &
UI_PID=$!
echo "✅ UI started (PID: $UI_PID)"
echo "   UI: http://localhost:3000"

cd ../..

echo ""
echo -e "${GREEN}=================================================="
echo "✅ All services started!"
echo "==================================================${NC}"
echo ""
echo "Services:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - UI: http://localhost:3000"
echo ""
echo "To stop services, press Ctrl+C or run:"
echo "  kill $API_PID $UI_PID"
echo ""
echo "To create an API key, run:"
echo "  cd services/api && python3 create_api_key.py"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $API_PID $UI_PID 2>/dev/null; exit" INT TERM

wait

