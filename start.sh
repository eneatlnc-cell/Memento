#!/bin/bash
#
# Creative AI Platform - One-Click Startup Script (Linux/macOS)
#
# Usage: bash start.sh
#

set -e

# ── Color definitions ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ── Helper functions ───────────────────────────────────────────────
print_step()  { echo -e "${CYAN}[STEP]${NC} $1"; }
print_ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
print_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERR]${NC}  $1"; }
print_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed. Please install $1 $2 first."
        return 1
    fi
    print_ok "$1 found: $($1 --version 2>&1 | head -1)"
}

# ── Banner ─────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                      ║${NC}"
echo -e "${CYAN}║${NC}       ${GREEN}Creative AI Platform${NC} - One-Click Setup       ${CYAN}║${NC}"
echo -e "${CYAN}║                                                      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Check prerequisites ────────────────────────────────────
print_step "Checking prerequisites..."

# Check Python 3.10+
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1)
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)" 2>&1)
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)" 2>&1)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    print_error "Python 3.10+ is required. Found: $PYTHON_VERSION"
    exit 1
fi
print_ok "Python $PYTHON_VERSION found"

# Check Node.js 18+
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi
NODE_VERSION=$(node -v 2>&1 | sed 's/v//')
NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
if [ "$NODE_MAJOR" -lt 18 ]; then
    print_error "Node.js 18+ is required. Found: v$NODE_VERSION"
    exit 1
fi
print_ok "Node.js v$NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed."
    exit 1
fi
print_ok "npm found"

# ── Step 2: Create virtual environment ─────────────────────────────
print_step "Setting up Python virtual environment..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_ok "Virtual environment created"
else
    print_ok "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_ok "Virtual environment activated"

# ── Step 3: Install backend dependencies ───────────────────────────
print_step "Installing backend dependencies..."

if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt -q
    print_ok "Backend dependencies installed"
else
    print_warn "backend/requirements.txt not found, skipping backend dependency installation"
fi

# ── Step 4: Copy .env.example to .env ──────────────────────────────
print_step "Setting up environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_ok ".env created from .env.example"

        # ── Auto-generate security keys ─────────────────────────────
        print_info "Generating JWT_SECRET..."
        JWT_SECRET=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|" .env
        print_ok "JWT_SECRET generated"

        print_info "Generating ENCRYPTION_KEY..."
        ENCRYPTION_KEY=$($PYTHON_CMD -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
        sed -i "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|" .env
        print_ok "ENCRYPTION_KEY generated"

        print_warn "Please review .env and set AGNES_API_KEY and DEFAULT_ADMIN_PASSWORD"
    else
        print_warn ".env.example not found, skipping .env creation"
    fi
else
    print_ok ".env already exists"
    # Check if keys are still placeholders
    if grep -q "JWT_SECRET=change-me" .env 2>/dev/null; then
        print_info "Regenerating JWT_SECRET..."
        JWT_SECRET=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|" .env
        print_ok "JWT_SECRET regenerated"
    fi
    if grep -q "ENCRYPTION_KEY=change-me" .env 2>/dev/null; then
        print_info "Regenerating ENCRYPTION_KEY..."
        ENCRYPTION_KEY=$($PYTHON_CMD -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
        sed -i "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|" .env
        print_ok "ENCRYPTION_KEY regenerated"
    fi
fi

# ── Step 5: Start backend (uvicorn, auto-initializes database) ─────
print_step "Starting backend server..."

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

if [ -f "backend/main.py" ]; then
    uvicorn backend.main:app --host "$HOST" --port "$PORT" --reload &
    BACKEND_PID=$!
    print_ok "Backend server starting on http://${HOST}:${PORT} (PID: $BACKEND_PID)"
else
    print_warn "backend/main.py not found, skipping backend startup"
    BACKEND_PID=""
fi

# Wait a moment for backend to start
sleep 2

# ── Step 7: Install frontend dependencies ──────────────────────────
print_step "Installing frontend dependencies..."

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    npm install --silent
    print_ok "Frontend dependencies installed"
    cd "$SCRIPT_DIR"
else
    print_warn "frontend/package.json not found, skipping frontend dependency installation"
fi

# ── Step 8: Start frontend dev server ──────────────────────────────
print_step "Starting frontend development server..."

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    print_ok "Frontend dev server starting (PID: $FRONTEND_PID)"
    cd "$SCRIPT_DIR"
else
    print_warn "frontend directory not found, skipping frontend startup"
    FRONTEND_PID=""
fi

# ── Step 9: Output access addresses ────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               All services started!                  ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  Backend API:   http://${HOST}:${PORT}                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  API Docs:      http://${HOST}:${PORT}/docs             ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Frontend:      http://localhost:5173                 ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
print_info "Press Ctrl+C to stop all services."

# ── Cleanup on exit ────────────────────────────────────────────────
cleanup() {
    echo ""
    print_info "Shutting down services..."
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
    print_ok "All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for background processes
wait