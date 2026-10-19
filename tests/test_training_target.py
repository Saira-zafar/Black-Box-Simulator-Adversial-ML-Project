import pytest
import sys
import os
from starlette.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "training_target")))

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "sandbox" in data["environment"]


def test_info_endpoint():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert len(data["scenarios"]) == 5


def test_auth_boundary_vulnerable_and_remediated():
    # Vulnerable endpoint allows unauthenticated access
    vuln_res = client.get("/api/vulnerable/user/settings")
    assert vuln_res.status_code == 200
    assert "internal_api_key" in vuln_res.json()

    # Remediated endpoint rejects missing token with 401
    rem_res_fail = client.get("/api/remediated/user/settings")
    assert rem_res_fail.status_code == 401

    # Remediated endpoint accepts valid token
    rem_res_ok = client.get(
        "/api/remediated/user/settings",
        headers={"Authorization": "Bearer valid_sandbox_auth_token_999"}
    )
    assert rem_res_ok.status_code == 200
    assert rem_res_ok.json()["username"] == "authorized_user"


def test_input_validation_vulnerable_and_remediated():
    # Vulnerable endpoint allows negative quantity business logic flaw
    vuln_res = client.post(
        "/api/vulnerable/calculate-discount",
        json={"price": 100, "quantity": -5}
    )
    assert vuln_res.status_code == 200
    assert "anomaly" in vuln_res.json()

    # Remediated endpoint rejects negative quantity with 422
    rem_res_fail = client.post(
        "/api/remediated/calculate-discount",
        json={"price": 100, "quantity": -5}
    )
    assert rem_res_fail.status_code == 422

    # Remediated endpoint accepts valid payload
    rem_res_ok = client.post(
        "/api/remediated/calculate-discount",
        json={"price": 100, "quantity": 2, "discount_code": "SANDBOX10"}
    )
    assert rem_res_ok.status_code == 200
    assert rem_res_ok.json()["total"] == 180.0


def test_session_security_vulnerable_and_remediated():
    # Vulnerable endpoint returns insecure cookie without HttpOnly
    vuln_res = client.post("/api/vulnerable/auth/session")
    assert vuln_res.status_code == 200
    raw_cookie_header = vuln_res.headers.get("set-cookie", "")
    assert "HttpOnly" not in raw_cookie_header

    # Remediated endpoint returns hardened cookie with HttpOnly & SameSite=lax
    rem_res = client.post("/api/remediated/auth/session")
    assert rem_res.status_code == 200
    cookie_header = rem_res.headers.get("set-cookie", "")
    assert "httponly" in cookie_header.lower()
    assert "samesite=lax" in cookie_header.lower()


def test_rate_limiting_remediated():
    # Remediated endpoint throttles after 5 rapid requests
    responses = []
    for _ in range(7):
        res = client.post("/api/remediated/auth/login-probe")
        responses.append(res.status_code)
    assert 429 in responses


def test_api_authorization_idor():
    # Vulnerable endpoint allows reading Bob's document (ID 202) without auth
    vuln_res = client.get("/api/vulnerable/documents/202")
    assert vuln_res.status_code == 200
    assert vuln_res.json()["owner_id"] == "user_bob"

    # Remediated endpoint rejects Alice accessing Bob's document
    rem_res_denied = client.get(
        "/api/remediated/documents/202",
        headers={"Authorization": "Bearer alice_token"}
    )
    assert rem_res_denied.status_code == 403

    # Remediated endpoint allows Alice accessing Alice's document (ID 101)
    rem_res_ok = client.get(
        "/api/remediated/documents/101",
        headers={"Authorization": "Bearer alice_token"}
    )
    assert rem_res_ok.status_code == 200
    assert rem_res_ok.json()["owner_id"] == "user_alice"
