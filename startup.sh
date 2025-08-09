#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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


# Check Python version and create virtual environment
echo -e "${GREEN}Checking Python version and creating virtual environment...${NC}"
cd backend

# Check if we have a compatible Python version
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3; do
    if command -v "$cmd" &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | grep -oE '3\.[0-9]+')
        if [[ "$VERSION" == "3.11" || "$VERSION" == "3.10" || "$VERSION" == "3.9" ]]; then
            PYTHON_CMD="$cmd"
            echo -e "${BLUE}Using $cmd (Python $($cmd --version 2>&1 | cut -d' ' -f2))${NC}"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}No compatible Python version found (3.9-3.11 recommended)${NC}"
    echo -e "${BLUE}Current python3 version: $(python3 --version)${NC}"
    echo -e "${BLUE}This may cause build issues. Consider installing Python 3.11${NC}"
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -m venv .venv
source .venv/bin/activate

# Upgrade pip and install build tools first
echo -e "${BLUE}Upgrading pip and installing build tools...${NC}"
pip install --upgrade pip
pip install --upgrade setuptools wheel build

# Install core dependencies first to avoid build issues
echo -e "${BLUE}Installing core dependencies...${NC}"
pip install numpy pandas

# Install requirements
echo -e "${BLUE}Installing Python dependencies...${NC}"
if ! pip install -r requirements.txt; then
    echo -e "${RED}Failed to install Python dependencies. Check the output above for errors.${NC}"
    exit 1
fi

# Install playwright browsers
echo -e "${BLUE}Installing Playwright browsers...${NC}"
playwright install chromium
cd ..


# Start Backend
echo -e "${GREEN}Starting FastAPI backend...${NC}"
cd backend
source .venv/bin/activate

# Check if all dependencies are available
echo -e "${BLUE}Checking backend dependencies...${NC}"
python -c "import faiss; import fastapi; import uvicorn; print('✅ All critical dependencies available')" || {
    echo -e "${RED}❌ Missing critical dependencies. Please check the installation output above.${NC}"
    exit 1
}

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