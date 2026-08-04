#!/usr/bin/env python3
"""
Creative AI Platform - Cross-Platform One-Click Startup Script

Usage:
    python start.py              # Full setup and start
    python start.py --check      # Check prerequisites only
    python start.py --backend    # Start backend only
    python start.py --frontend   # Start frontend only
"""

import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path


# ── Color support ───────────────────────────────────────────────────

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def supports_color():
        """Check if the terminal supports ANSI color codes."""
        if platform.system() == 'Windows':
            try:
                # Windows 10+ supports ANSI via VT processing
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                return False
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


USE_COLORS = Colors.supports_color()


def color(text: str, code: str) -> str:
    """Wrap text with color code if colors are supported."""
    if USE_COLORS:
        return f"{code}{text}{Colors.NC}"
    return text


def print_step(msg: str):
    print(f"  {color('[STEP]', Colors.CYAN)} {msg}")


def print_ok(msg: str):
    print(f"  {color('[OK]', Colors.GREEN)}   {msg}")


def print_warn(msg: str):
    print(f"  {color('[WARN]', Colors.YELLOW)} {msg}")


def print_error(msg: str):
    print(f"  {color('[ERR]', Colors.RED)}  {msg}")


def print_info(msg: str):
    print(f"  {color('[INFO]', Colors.BLUE)} {msg}")


# ── Platform detection ──────────────────────────────────────────────

SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == 'Windows'
IS_MACOS = SYSTEM == 'Darwin'
IS_LINUX = SYSTEM == 'Linux'

# ── Paths ───────────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / 'backend'
FRONTEND_DIR = ROOT_DIR / 'frontend'
VENV_DIR = ROOT_DIR / 'venv'
ENV_FILE = ROOT_DIR / '.env'
ENV_EXAMPLE_FILE = ROOT_DIR / '.env.example'


def get_venv_python() -> str:
    """Get path to Python executable in virtual environment."""
    if IS_WINDOWS:
        return str(VENV_DIR / 'Scripts' / 'python.exe')
    return str(VENV_DIR / 'bin' / 'python')


def get_venv_pip() -> str:
    """Get path to pip executable in virtual environment."""
    if IS_WINDOWS:
        return str(VENV_DIR / 'Scripts' / 'pip.exe')
    return str(VENV_DIR / 'bin' / 'pip')


def get_venv_activate_cmd() -> list:
    """Get the shell command to activate the virtual environment."""
    if IS_WINDOWS:
        return [str(VENV_DIR / 'Scripts' / 'activate.bat')]
    return [f"source {VENV_DIR / 'bin' / 'activate'}"]


# ── Prerequisite checks ─────────────────────────────────────────────

def find_python() -> str | None:
    """Find a suitable Python 3.10+ executable."""
    candidates = ['python3.10', 'python3', 'python'] if not IS_WINDOWS else ['python3.10', 'python3', 'python']
    for cmd in candidates:
        path = shutil.which(cmd)
        if path:
            return path
    return None


def check_python_version(python_path: str) -> tuple[bool, str]:
    """Check if Python version is 3.10+."""
    try:
        result = subprocess.run(
            [python_path, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'],
            capture_output=True, text=True, timeout=10
        )
        version = result.stdout.strip()
        major, minor = version.split('.')
        if int(major) >= 3 and int(minor) >= 10:
            return True, version
        return False, version
    except Exception:
        return False, 'unknown'


def check_node_version() -> tuple[bool, str]:
    """Check if Node.js version is 18+."""
    try:
        result = subprocess.run(['node', '-v'], capture_output=True, text=True, timeout=10)
        version = result.stdout.strip().lstrip('v')
        major = int(version.split('.')[0])
        return major >= 18, version
    except Exception:
        return False, 'unknown'


def check_prerequisites() -> bool:
    """Check all prerequisites. Returns True if all pass."""
    print_step("Checking prerequisites...")
    all_ok = True

    # Python
    python_path = find_python()
    if python_path is None:
        print_error("Python is not installed. Please install Python 3.10+.")
        all_ok = False
    else:
        ok, version = check_python_version(python_path)
        if ok:
            print_ok(f"Python {version} found ({python_path})")
        else:
            print_error(f"Python 3.10+ is required. Found: {version}")
            all_ok = False

    # Node.js
    ok, version = check_node_version()
    if ok:
        print_ok(f"Node.js v{version} found")
    else:
        print_error("Node.js 18+ is required.")
        all_ok = False

    # npm
    if shutil.which('npm'):
        print_ok("npm found")
    else:
        print_error("npm is not installed.")
        all_ok = False

    return all_ok


# ── Setup steps ─────────────────────────────────────────────────────

def setup_virtualenv() -> bool:
    """Create virtual environment if it doesn't exist."""
    print_step("Setting up Python virtual environment...")
    python_path = find_python()
    if python_path is None:
        print_error("Cannot find Python to create virtual environment.")
        return False

    if VENV_DIR.exists():
        print_ok("Virtual environment already exists")
        return True

    try:
        subprocess.run([python_path, '-m', 'venv', str(VENV_DIR)], check=True)
        print_ok("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def install_backend_deps() -> bool:
    """Install backend Python dependencies."""
    print_step("Installing backend dependencies...")
    req_file = BACKEND_DIR / 'requirements.txt'
    if not req_file.exists():
        print_warn("backend/requirements.txt not found, skipping")
        return True

    pip = get_venv_pip()
    try:
        subprocess.run([pip, 'install', '-r', str(req_file), '-q'], check=True)
        print_ok("Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install backend dependencies: {e}")
        return False


def setup_env_file() -> bool:
    """Copy .env.example to .env if .env doesn't exist."""
    print_step("Setting up environment configuration...")
    if ENV_FILE.exists():
        print_ok(".env already exists")
        return True

    if not ENV_EXAMPLE_FILE.exists():
        print_warn(".env.example not found, skipping")
        return True

    try:
        shutil.copy(ENV_EXAMPLE_FILE, ENV_FILE)
        print_ok(".env created from .env.example")
        print_warn("Please review and update .env with your actual configuration values")
        return True
    except OSError as e:
        print_error(f"Failed to create .env: {e}")
        return False


def init_database() -> bool:
    """Initialize the database."""
    print_step("Initializing database...")
    init_script = BACKEND_DIR / 'init_db.py'
    if not init_script.exists():
        print_warn("backend/init_db.py not found, skipping")
        return True

    python = get_venv_python()
    try:
        subprocess.run([python, str(init_script)], check=True, cwd=str(ROOT_DIR))
        print_ok("Database initialized")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Database initialization failed: {e}")
        return False


def install_frontend_deps() -> bool:
    """Install frontend Node.js dependencies."""
    print_step("Installing frontend dependencies...")
    pkg_json = FRONTEND_DIR / 'package.json'
    if not pkg_json.exists():
        print_warn("frontend/package.json not found, skipping")
        return True

    try:
        subprocess.run(['npm', 'install', '--silent'], check=True, cwd=str(FRONTEND_DIR))
        print_ok("Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install frontend dependencies: {e}")
        return False


# ── Service management ──────────────────────────────────────────────

BACKEND_PROCESS = None
FRONTEND_PROCESS = None


def start_backend() -> bool:
    """Start the backend server."""
    global BACKEND_PROCESS
    print_step("Starting backend server...")

    main_py = BACKEND_DIR / 'main.py'
    if not main_py.exists():
        print_warn("backend/main.py not found, skipping")
        return True

    host = os.environ.get('HOST', '0.0.0.0')
    port = os.environ.get('PORT', '8000')

    try:
        BACKEND_PROCESS = subprocess.Popen(
            ['uvicorn', 'backend.main:app', '--host', host, '--port', str(port), '--reload'],
            cwd=str(ROOT_DIR),
        )
        print_ok(f"Backend server starting on http://{host}:{port} (PID: {BACKEND_PROCESS.pid})")
        return True
    except FileNotFoundError:
        print_error("uvicorn not found. Please install backend dependencies first.")
        return False
    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        return False


def start_frontend() -> bool:
    """Start the frontend dev server."""
    global FRONTEND_PROCESS
    print_step("Starting frontend development server...")

    pkg_json = FRONTEND_DIR / 'package.json'
    if not pkg_json.exists():
        print_warn("frontend/package.json not found, skipping")
        return True

    try:
        if IS_WINDOWS:
            FRONTEND_PROCESS = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=str(FRONTEND_DIR),
                shell=True,
            )
        else:
            FRONTEND_PROCESS = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=str(FRONTEND_DIR),
            )
        print_ok(f"Frontend dev server starting (PID: {FRONTEND_PROCESS.pid})")
        return True
    except FileNotFoundError:
        print_error("npm not found.")
        return False
    except Exception as e:
        print_error(f"Failed to start frontend: {e}")
        return False


def stop_services():
    """Stop all running services."""
    global BACKEND_PROCESS, FRONTEND_PROCESS
    print_info("Shutting down services...")

    for proc, name in [(BACKEND_PROCESS, 'Backend'), (FRONTEND_PROCESS, 'Frontend')]:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            print_ok(f"{name} stopped")

    BACKEND_PROCESS = None
    FRONTEND_PROCESS = None


def print_banner():
    """Print the startup banner."""
    print()
    print(f"  {color('Creative AI Platform', Colors.GREEN + Colors.BOLD)} - One-Click Setup")
    print(f"  Platform: {color(SYSTEM, Colors.MAGENTA)}")
    print(f"  Root:     {color(str(ROOT_DIR), Colors.BLUE)}")
    print()


def print_summary():
    """Print the final summary with access URLs."""
    host = os.environ.get('HOST', '0.0.0.0')
    port = os.environ.get('PORT', '8000')
    print()
    print(f"  {color('All services started!', Colors.GREEN + Colors.BOLD)}")
    print(f"  {'─' * 50}")
    print(f"  Backend API:   {color(f'http://{host}:{port}', Colors.CYAN)}")
    print(f"  API Docs:      {color(f'http://{host}:{port}/docs', Colors.CYAN)}")
    print(f"  Frontend:      {color('http://localhost:5173', Colors.CYAN)}")
    print(f"  {'─' * 50}")
    print(f"  {color('Press Ctrl+C to stop all services.', Colors.YELLOW)}")
    print()


# ── Main entry point ────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Creative AI Platform - One-Click Startup Script',
    )
    parser.add_argument('--check', action='store_true', help='Check prerequisites only')
    parser.add_argument('--backend', action='store_true', help='Start backend only')
    parser.add_argument('--frontend', action='store_true', help='Start frontend only')
    parser.add_argument('--skip-frontend', action='store_true', help='Skip frontend setup')
    parser.add_argument('--skip-backend', action='store_true', help='Skip backend setup')
    args = parser.parse_args()

    print_banner()

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    if args.check:
        print_ok("All prerequisites satisfied!")
        return

    # Setup virtual environment
    if not setup_virtualenv():
        sys.exit(1)

    # Backend setup
    if not args.skip_backend and not args.frontend:
        if not install_backend_deps():
            sys.exit(1)
        if not setup_env_file():
            sys.exit(1)
        if not init_database():
            sys.exit(1)

    # Frontend setup
    if not args.skip_frontend and not args.backend:
        if not install_frontend_deps():
            sys.exit(1)

    # Start services
    if args.backend:
        if not start_backend():
            sys.exit(1)
        print_info("Backend is running. Press Ctrl+C to stop.")
        try:
            while BACKEND_PROCESS and BACKEND_PROCESS.poll() is None:
                time.sleep(0.5)
        except KeyboardInterrupt:
            stop_services()
        return

    if args.frontend:
        if not start_frontend():
            sys.exit(1)
        print_info("Frontend is running. Press Ctrl+C to stop.")
        try:
            while FRONTEND_PROCESS and FRONTEND_PROCESS.poll() is None:
                time.sleep(0.5)
        except KeyboardInterrupt:
            stop_services()
        return

    # Full startup
    if not start_backend():
        sys.exit(1)

    # Wait for backend to initialize
    time.sleep(2)

    if not start_frontend():
        sys.exit(1)

    print_summary()

    # Keep running until Ctrl+C
    try:
        while True:
            if BACKEND_PROCESS and BACKEND_PROCESS.poll() is not None:
                print_error("Backend process exited unexpectedly")
                break
            if FRONTEND_PROCESS and FRONTEND_PROCESS.poll() is not None:
                print_error("Frontend process exited unexpectedly")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        stop_services()


if __name__ == '__main__':
    main()