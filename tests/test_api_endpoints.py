import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from main import app
from app.db.init_db import init_db

# Initialize DB for tests
init_db()
client = TestClient(app)


def test_backend_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["sandbox_enforced"] is True


def test_list_scenarios():
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) == 5
    scenario_ids = [s["id"] for s in scenarios]
    assert "auth-boundary" in scenario_ids
    assert "input-validation" in scenario_ids
    assert "session-security" in scenario_ids
    assert "rate-limiting" in scenario_ids
    assert "api-authorization" in scenario_ids


def test_get_scenario_detail():
    res = client.get("/api/scenarios/auth-boundary")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "auth-boundary"
    assert data["cwe_id"] == "CWE-287"
    assert len(data["steps"]) == 3


def test_target_health_blocks_external_url():
    """Verify that target health check blocks external targets."""
    res = client.get("/api/target/health?url=http://8.8.8.8")
    assert res.status_code == 400
    assert "Safety Guardrail" in res.json()["detail"]


def test_simulation_run_blocks_external_target():
    """Verify that triggering a simulation against an external domain is rejected."""
    payload = {
        "scenario_id": "auth-boundary",
        "target_url": "http://example.com/api",
        "target_mode": "vulnerable"
    }
    res = client.post("/api/simulations/run", json=payload)
    assert res.status_code == 400
    assert "Safety Guardrail Blocked Target" in res.json()["detail"]


def test_simulation_run_blocks_metadata_ip():
    """Verify that targeting AWS/GCP cloud metadata IP is rejected."""
    payload = {
        "scenario_id": "auth-boundary",
        "target_url": "http://169.254.169.254/meta-data",
        "target_mode": "vulnerable"
    }
    res = client.post("/api/simulations/run", json=payload)
    assert res.status_code == 400
    assert "Safety Guardrail Blocked Target" in res.json()["detail"]
