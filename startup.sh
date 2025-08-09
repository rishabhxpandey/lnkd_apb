#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Proxy bypass for company network (keeps localhost traffic local)
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo -e "${BLUE}LinkedIn Interview Prep AI - Starting Services...${NC}"
echo -e "${BLUE}Proxy bypass configured for localhost connections${NC}"
echo ""

# Remove existing Python virtual environment if it exists
if [ -d "backend/.venv" ]; then
    echo -e "${BLUE}Removing existing Python virtual environment...${NC}"
    rm -rf backend/.venv
fi


# Check if backend virtual environment exists
echo -e "${GREEN}Creating Python virtual environment...${NC}"
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
clear

# Start Backend
echo -e "${GREEN}Starting FastAPI backend...${NC}"
cd backend
source .venv/bin/activate
uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo -e "${GREEN}Starting React frontend...${NC}"
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

# Cleanup on exit
trap "echo -e '\n${BLUE}Shutting down services...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo ""
echo -e "${GREEN}✅ Project is running!${NC}"
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
wait 