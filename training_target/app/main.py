"""
Deliberately Vulnerable Local Training Application.

PURPOSE:
Educational sandbox serving as the SOLE target for the Black-Box Attack Simulator.
Provides both deliberately misconfigured/vulnerable endpoints and hardened remediated
counterpart endpoints for security testing scenarios.
"""

from fastapi import FastAPI, Request, Response, HTTPException, status, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import time
import uuid
from typing import Optional, Dict, List

app = FastAPI(
    title="Black-Box Training Target Sandbox",
    description="Deliberately vulnerable educational service for local security simulation.",
    version="1.0.0"
)

# In-memory store for rate-limiting simulation
rate_limit_records: Dict[str, List[float]] = {}

# In-memory documents store for BOLA/IDOR simulation
DOCUMENTS_DB = {
    101: {
        "id": 101,
        "owner_id": "user_alice",
        "title": "Alice's Public Project Notes",
        "confidentiality": "Low",
        "content": "Meeting agenda for Monday morning team standup."
    },
    202: {
        "id": 202,
        "owner_id": "user_bob",
        "title": "Bob's Confidential Financial Ledger",
        "confidentiality": "Restricted",
        "content": "CONFIDENTIAL: Q3 Financial audit results and bank account routing #4492-1082."
    },
    303: {
        "id": 303,
        "owner_id": "user_charlie",
        "title": "Charlie's Internal Security Keys",
        "confidentiality": "Critical",
        "content": "SSH Private Key fingerprint: SHA256:d8a7c6f0... DO NOT SHARE."
    }
}


@app.get("/health")
def health_check():
    """Health check endpoint to verify target service status."""
    return {
        "status": "online",
        "service": "Local Training Target Sandbox",
        "version": "1.0.0",
        "environment": "local_sandbox"
    }


@app.get("/api/info")
def service_info():
    """Returns directory of available vulnerable and remediated routes."""
    return {
        "scenarios": [
            {
                "id": "auth-boundary",
                "name": "Authentication Boundary",
                "vulnerable_route": "/api/vulnerable/user/settings",
                "remediated_route": "/api/remediated/user/settings"
            },
            {
                "id": "input-validation",
                "name": "Input Validation & Boundary Testing",
                "vulnerable_route": "/api/vulnerable/calculate-discount",
                "remediated_route": "/api/remediated/calculate-discount"
            },
            {
                "id": "session-security",
                "name": "Session Security & Cookie Attributes",
                "vulnerable_route": "/api/vulnerable/auth/session",
                "remediated_route": "/api/remediated/auth/session"
            },
            {
                "id": "rate-limiting",
                "name": "Rate-Limit Threshold Behavior",
                "vulnerable_route": "/api/vulnerable/auth/login-probe",
                "remediated_route": "/api/remediated/auth/login-probe"
            },
            {
                "id": "api-authorization",
                "name": "API Authorization / BOLA (IDOR)",
                "vulnerable_route": "/api/vulnerable/documents/{id}",
                "remediated_route": "/api/remediated/documents/{id}"
            }
        ]
    }


# ==========================================
# 1. AUTHENTICATION BOUNDARY
# ==========================================

@app.get("/api/vulnerable/user/settings")
def get_user_settings_vulnerable(authorization: Optional[str] = Header(None)):
    """
    VULNERABLE: Does not check or validate the Authorization header.
    Returns sensitive user settings to any unauthenticated caller.
    """
    return {
        "user_id": 1,
        "username": "admin",
        "email": "admin@local-sandbox.internal",
        "role": "SuperAdministrator",
        "debug_mode": True,
        "internal_api_key": "sec_live_sandbox_k7829910f"
    }


@app.get("/api/remediated/user/settings")
def get_user_settings_remediated(authorization: Optional[str] = Header(None)):
    """
    REMEDIATED: Strictly validates Bearer token and returns 401 Unauthorized if invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token. Bearer scheme required.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = authorization.split(" ")[1]
    if token != "valid_sandbox_auth_token_999":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is expired or invalid.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {
        "user_id": 1,
        "username": "authorized_user",
        "email": "student@local-sandbox.internal",
        "role": "StudentViewer",
        "debug_mode": False
    }


# ==========================================
# 2. INPUT VALIDATION & ERROR HANDLING
# ==========================================

@app.post("/api/vulnerable/calculate-discount")
async def calculate_discount_vulnerable(request: Request):
    """
    VULNERABLE: Blindly accepts raw JSON, allows negative quantity, division by zero,
    and returns raw unhandled 500 stack traces upon bad input.
    """
    body = await request.json()
    price = body.get("price")
    quantity = body.get("quantity")

    # Deliberate vulnerability: No boundary or type checking
    # If quantity is negative or 0 or invalid, triggers raw python crash
    if quantity == 0:
        # ZeroDivisionError crash
        res = price / quantity
    elif isinstance(quantity, (int, float)) and quantity < 0:
        # Business logic boundary flaw: negative total price
        return {
            "status": "success",
            "quantity": quantity,
            "unit_price": price,
            "total": price * quantity,
            "anomaly": "Negative total allowed! Business logic bypass."
        }
    elif isinstance(quantity, str):
        # Type flaw: causes TypeError crash leaking stack trace
        res = price * quantity + 1

    total = price * quantity
    return {"status": "success", "total": total}


class RemediatedDiscountRequest(BaseModel):
    price: float = Field(..., gt=0, le=100000, description="Price must be strictly positive")
    quantity: int = Field(..., gt=0, le=1000, description="Quantity must be between 1 and 1000")
    discount_code: Optional[str] = Field(None, max_length=20, pattern=r"^[A-Z0-9_-]+$")


@app.post("/api/remediated/calculate-discount")
def calculate_discount_remediated(payload: RemediatedDiscountRequest):
    """
    REMEDIATED: Strictly validates input data types and boundaries with Pydantic.
    Invalid inputs return clean 422 Unprocessable Entity with zero stack leakage.
    """
    discount = 0.0
    if payload.discount_code == "SANDBOX10":
        discount = 0.10
    total = round((payload.price * payload.quantity) * (1.0 - discount), 2)
    return {
        "status": "success",
        "price": payload.price,
        "quantity": payload.quantity,
        "discount_applied": f"{int(discount * 100)}%",
        "total": total
    }


# ==========================================
# 3. SESSION SECURITY
# ==========================================

@app.post("/api/vulnerable/auth/session")
def create_session_vulnerable(response: Response):
    """
    VULNERABLE: Issues insecure session cookie:
    - Missing HttpOnly (vulnerable to XSS theft)
    - Missing SameSite (vulnerable to CSRF)
    - Predictable sequential ID
    """
    predictable_id = "sess_1001"
    response.set_cookie(
        key="session_token",
        value=predictable_id,
        httponly=False,  # Insecure!
        samesite=None,   # Insecure!
        secure=False
    )
    return {
        "message": "Session created (Insecure configuration)",
        "session_id": predictable_id,
        "cookie_attributes": {
            "HttpOnly": False,
            "SameSite": "None",
            "Secure": False
        }
    }


@app.post("/api/remediated/auth/session")
def create_session_remediated(response: Response):
    """
    REMEDIATED: Issues secure cookie with HttpOnly, SameSite=Lax, and high-entropy token.
    """
    cryptographic_token = f"sess_{uuid.uuid4().hex}"
    response.set_cookie(
        key="session_token",
        value=cryptographic_token,
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=3600
    )
    return {
        "message": "Session created (Hardened configuration)",
        "cookie_attributes": {
            "HttpOnly": True,
            "SameSite": "Lax",
            "Secure": True,
            "Max-Age": 3600
        }
    }


# ==========================================
# 4. RATE LIMITING
# ==========================================

@app.post("/api/vulnerable/auth/login-probe")
def login_probe_vulnerable():
    """
    VULNERABLE: No rate limiting.
    Allows automated brute-force / rapid burst requests without penalty.
    """
    return {
        "status": "processed",
        "rate_limiting_enforced": False,
        "message": "Probe processed without throttle."
    }


@app.post("/api/remediated/auth/login-probe")
def login_probe_remediated(request: Request):
    """
    REMEDIATED: Enforces burst rate limit (Max 5 requests within 10-second sliding window).
    Returns HTTP 429 Too Many Requests with Retry-After header.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    current_time = time.time()
    window_seconds = 10.0
    max_requests = 5

    timestamps = rate_limit_records.get(client_ip, [])
    # Filter to timestamps within window
    timestamps = [t for t in timestamps if current_time - t < window_seconds]

    if len(timestamps) >= max_requests:
        retry_after = int(window_seconds - (current_time - timestamps[0])) + 1
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Too Many Requests",
                "detail": f"Rate limit exceeded. Maximum {max_requests} requests per {int(window_seconds)}s window.",
                "retry_after_seconds": max(1, retry_after)
            },
            headers={"Retry-After": str(max(1, retry_after))}
        )

    timestamps.append(current_time)
    rate_limit_records[client_ip] = timestamps

    return {
        "status": "processed",
        "rate_limiting_enforced": True,
        "requests_in_window": len(timestamps),
        "limit": max_requests
    }


# ==========================================
# 5. API AUTHORIZATION (BOLA / IDOR)
# ==========================================

@app.get("/api/vulnerable/documents/{doc_id}")
def get_document_vulnerable(doc_id: int):
    """
    VULNERABLE: Broken Object Level Authorization (IDOR/BOLA).
    Returns any document by ID without verifying if caller owns it.
    """
    doc = DOCUMENTS_DB.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@app.get("/api/remediated/documents/{doc_id}")
def get_document_remediated(doc_id: int, authorization: Optional[str] = Header(None)):
    """
    REMEDIATED: Checks tenant ownership. Only the authorized owner can view their document.
    Mock test user identity: 'user_alice'.
    """
    doc = DOCUMENTS_DB.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Caller identity extracted from auth token (mocked for educational sandbox)
    caller_user_id = "user_alice" if authorization == "Bearer alice_token" else "anonymous"

    if doc["owner_id"] != caller_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: You do not have permission to access document #{doc_id} belonging to '{doc['owner_id']}'."
        )

    return doc
