"""
Black-Box Attack Simulator - Local Sandbox Multi-Service Launcher.
Starts:
  1. Training Target Service on http://127.0.0.1:8001
  2. Simulator Backend on http://127.0.0.1:8000
  3. React Frontend on http://127.0.0.1:5173 (via vite dev server)
"""

import subprocess
import sys
import os
import time
import signal

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "Scripts", "python.exe")
NPM_CMD = "npm.cmd" if os.name == "nt" else "npm"


def main():
    print("=" * 65)
    print("  BLACK-BOX ATTACK SIMULATOR - EDUCATIONAL SANDBOX")
    print("  CRITICAL: Safe local testing only. Zero external access.")
    print("=" * 65)

    if not os.path.exists(VENV_PYTHON):
        print(f"[!] Virtual environment not found at {VENV_PYTHON}. Run setup first.")
        sys.exit(1)

    processes = []

    try:
        # 1. Start Training Target
        print("[1/3] Starting Training Target Service on http://127.0.0.1:8001...")
        target_proc = subprocess.Popen(
            [VENV_PYTHON, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
            cwd=os.path.join(ROOT_DIR, "training_target")
        )
        processes.append(target_proc)

        # 2. Start Simulator Backend
        print("[2/3] Starting Simulator Backend Engine on http://127.0.0.1:8000...")
        backend_proc = subprocess.Popen(
            [VENV_PYTHON, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=os.path.join(ROOT_DIR, "backend")
        )
        processes.append(backend_proc)

        time.sleep(1.5)

        # 3. Start Frontend Dev Server
        print("[3/3] Starting React Dashboard on http://127.0.0.1:5173...")
        frontend_proc = subprocess.Popen(
            [NPM_CMD, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
            cwd=os.path.join(ROOT_DIR, "frontend"),
            shell=(os.name == "nt")
        )
        processes.append(frontend_proc)

        print("\n" + "=" * 65)
        print("  All local sandbox services are running!")
        print("  - React Dashboard:   http://127.0.0.1:5173")
        print("  - Simulator Backend: http://127.0.0.1:8000")
        print("  - Training Target:   http://127.0.0.1:8001")
        print("  Press Ctrl+C to terminate all services safely.")
        print("=" * 65 + "\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down sandbox services...")
    finally:
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("All processes terminated.")


if __name__ == "__main__":
    main()
