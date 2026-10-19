# Black-Box Attack Simulator (Educational Sandbox)

A cybersecurity educational platform for students and security engineers to select predefined security test scenarios, execute safe black-box simulations against a local training target, and receive structured assessments with defensive remediations.

---

## 🔒 Safety Architecture & Local Sandboxing Guarantee

> **IMPORTANT SAFETY RESTRICTION**:
> - This simulator is **strictly constrained to local sandboxes** (`localhost`, `127.0.0.1`, `[::1]`, and internal Docker hostnames).
> - Under no circumstances does the engine scan, probe, attack, or interact with external internet hosts, internal corporate LANs, or cloud metadata endpoints.
> - The safety guardrail module (`backend/app/core/safety.py`) cryptographically parses and validates all target URLs before any socket or HTTP connection is initiated, raising `SecurityViolationError` on any unauthorized destination.
> - Automated regression tests (`tests/test_safety_guardrails.py`) verify that all non-local destinations are rejected.

---

## 🏗️ Architecture & Technology Stack

- **Backend**: Python FastAPI (`backend/`)
- **Database**: SQLite with SQLAlchemy ORM (`backend/simulator.db`)
- **Target Service**: Standalone FastAPI training service (`training_target/`) featuring vulnerable and remediated route pairs
- **Frontend**: React + Vite + Vanilla CSS (`frontend/`) with dark mode cybersecurity aesthetics
- **Testing**: Pytest with 24 automated unit and integration tests (`tests/`)
- **Containerization**: Docker Compose (`docker/`) with isolated bridge network

```
adversial/
├── backend/                  # FastAPI Simulator Backend
│   ├── app/
│   │   ├── api/routes.py     # REST endpoints for scenarios, runs, reports
│   │   ├── analyzer/         # Results & severity analyzer
│   │   ├── core/safety.py    # Strict loopback validation guardrail
│   │   ├── db/               # SQLite models & session management
│   │   ├── engine/           # Safe simulation runner & scenario registry
│   │   └── reports/          # Markdown and JSON report generator
│   ├── main.py               # Backend server entrypoint
│   └── requirements.txt
├── frontend/                 # React UI Dashboard
│   ├── src/
│   │   ├── components/       # Dashboard, Console, History, Catalog, Modals
│   │   ├── api.js            # API client
│   │   ├── App.jsx           # Main application shell
│   │   └── index.css         # Cyber-dark design system
│   └── package.json
├── training_target/          # Deliberately Vulnerable Local Service
│   ├── app/main.py           # Vulnerable and remediated endpoint pairs
│   └── requirements.txt
├── tests/                    # Automated Test Suite (Pytest)
│   ├── test_safety_guardrails.py   # Verifies external targets are blocked
│   ├── test_training_target.py     # Verifies target endpoint behaviors
│   ├── test_api_endpoints.py       # Verifies backend REST API & safety
│   └── test_simulation_engine.py   # Verifies runner, evaluator, reports
├── reports/                  # Generated assessment markdown reports
├── docker/                   # Docker Compose & Dockerfiles
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.target
└── run_simulator.py          # All-in-one local launcher
```

---

## 🎯 Educational Security Scenarios

| Scenario ID | Category | Target Vulnerable Route | Target Remediated Route | CWE & OWASP | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `auth-boundary` | Authentication | `/api/vulnerable/user/settings` | `/api/remediated/user/settings` | **CWE-287**<br>A07:2021 | Probes with missing, malformed, and forged tokens. Evaluates whether access control is enforced. |
| `input-validation` | Input Validation | `/api/vulnerable/calculate-discount` | `/api/remediated/calculate-discount` | **CWE-20**<br>A03:2021 | Tests boundary values (negative quantity, 0, string types) to detect logic errors and stack trace leaks. |
| `session-security` | Session Security | `/api/vulnerable/auth/session` | `/api/remediated/auth/session` | **CWE-614**<br>A07:2021 | Audits session cookie flags (`HttpOnly` to stop XSS theft, `SameSite` to mitigate CSRF, high-entropy ID). |
| `rate-limiting` | Rate Limiting | `/api/vulnerable/auth/login-probe` | `/api/remediated/auth/login-probe` | **CWE-799**<br>A04:2021 | Dispatches rapid bursts of requests to determine if brute-force frequency thresholds are enforced (HTTP 429). |
| `api-authorization` | Access Control | `/api/vulnerable/documents/202` | `/api/remediated/documents/202` | **CWE-639**<br>A01:2021 | Broken Object Level Authorization (IDOR/BOLA): checks if user Alice can access confidential records belonging to user Bob. |

---

## 🚀 Getting Started (Local Development)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Install Dependencies
```bash
# Python backend & target
py -m venv .venv
.venv\Scripts\pip.exe install -r backend/requirements.txt

# Frontend
cd frontend
npm.cmd install
cd ..
```

### 3. Run Automated Tests
```bash
.venv\Scripts\pytest.exe -v tests/
```
*All 24 tests will execute, confirming that external network access is blocked and target scenarios operate reliably.*

### 4. Start the Application
Run all services with the single launcher script:
```bash
py run_simulator.py
```
Or start services individually in separate terminals:
```bash
# Terminal 1: Training Target (Port 8001)
.venv\Scripts\uvicorn.exe training_target.app.main:app --port 8001

# Terminal 2: Backend Engine (Port 8000)
.venv\Scripts\uvicorn.exe backend.main:app --port 8000

# Terminal 3: Frontend Dashboard (Port 5173)
cd frontend && npm.cmd run dev
```

Open your browser to **`http://localhost:5173`** to access the simulator.

---

## 🐳 Docker Deployment

To run in fully isolated Docker containers on an internal bridge network:

```bash
cd docker
docker compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Isolated Target: `http://localhost:8001`
