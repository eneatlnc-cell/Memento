@echo off
REM  Creative AI Platform - One-Click Startup Script (Windows)
REM  Usage: start.bat

setlocal enabledelayedexpansion

REM ── Banner ─────────────────────────────────────────────────────────
echo.
echo ==========================================================
echo        Creative AI Platform - One-Click Setup
echo ==========================================================
echo.

REM ── Step 1: Check Python 3.10+ ────────────────────────────────────
echo [STEP] Checking Python 3.10+...

where python3.10 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3.10
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        where python >nul 2>&1
        if %errorlevel% equ 0 (
            set PYTHON_CMD=python
        ) else (
            echo [ERR]  Python is not installed. Please install Python 3.10+.
            pause
            exit /b 1
        )
    )
)

%PYTHON_CMD% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERR]  Python 3.10+ is required.
    pause
    exit /b 1
)
echo [OK]   Python found

REM ── Step 2: Check Node.js 18+ ─────────────────────────────────────
echo [STEP] Checking Node.js 18+...

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERR]  Node.js is not installed. Please install Node.js 18+.
    pause
    exit /b 1
)

for /f "tokens=1 delims=." %%a in ('node -v') do set NODE_MAJOR=%%a
set NODE_MAJOR=%NODE_MAJOR:v=%
if %NODE_MAJOR% lss 18 (
    echo [ERR]  Node.js 18+ is required. Found: v%NODE_MAJOR%
    pause
    exit /b 1
)
echo [OK]   Node.js found

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERR]  npm is not installed.
    pause
    exit /b 1
)
echo [OK]   npm found

REM ── Step 3: Create virtual environment ────────────────────────────
echo [STEP] Setting up Python virtual environment...

if not exist "venv" (
    %PYTHON_CMD% -m venv venv
    echo [OK]   Virtual environment created
) else (
    echo [OK]   Virtual environment already exists
)

REM ── Activate virtual environment
call venv\Scripts\activate.bat
echo [OK]   Virtual environment activated

REM ── Step 4: Install backend dependencies ──────────────────────────
echo [STEP] Installing backend dependencies...

if exist "backend\requirements.txt" (
    pip install -r backend\requirements.txt -q
    echo [OK]   Backend dependencies installed
) else (
    echo [WARN] backend\requirements.txt not found, skipping
)

REM ── Step 5: Copy .env.example to .env ─────────────────────────────
echo [STEP] Setting up environment configuration...

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK]   .env created from .env.example
        echo [WARN] Please review and update .env with your actual values
    ) else (
        echo [WARN] .env.example not found, skipping
    )
) else (
    echo [OK]   .env already exists
)

REM ── Step 6: Initialize database ───────────────────────────────────
echo [STEP] Initializing database...

if exist "backend\init_db.py" (
    %PYTHON_CMD% backend\init_db.py
    echo [OK]   Database initialized
) else (
    echo [WARN] backend\init_db.py not found, skipping
)

REM ── Step 7: Start backend (uvicorn) ───────────────────────────────
echo [STEP] Starting backend server...

if exist "backend\main.py" (
    start "Creative AI - Backend" cmd /c "uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
    echo [OK]   Backend server starting on http://0.0.0.0:8000
) else (
    echo [WARN] backend\main.py not found, skipping
)

REM ── Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM ── Step 8: Install frontend dependencies ─────────────────────────
echo [STEP] Installing frontend dependencies...

if exist "frontend\package.json" (
    cd frontend
    call npm install --silent
    echo [OK]   Frontend dependencies installed
    cd ..
) else (
    echo [WARN] frontend\package.json not found, skipping
)

REM ── Step 9: Start frontend dev server ─────────────────────────────
echo [STEP] Starting frontend development server...

if exist "frontend\package.json" (
    cd frontend
    start "Creative AI - Frontend" cmd /c "npm run dev"
    echo [OK]   Frontend dev server starting
    cd ..
) else (
    echo [WARN] frontend directory not found, skipping
)

REM ── Output access addresses ───────────────────────────────────────
echo.
echo ==========================================================
echo                All services started!
echo ----------------------------------------------------------
echo   Backend API:   http://0.0.0.0:8000
echo   API Docs:      http://0.0.0.0:8000/docs
echo   Frontend:      http://localhost:5173
echo ==========================================================
echo.
echo Press any key to exit this launcher (services will keep running).
pause >nul
endlocal