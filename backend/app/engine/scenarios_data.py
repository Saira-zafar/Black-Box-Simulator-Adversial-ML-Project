"""
Predefined Educational Security Scenarios Data.
Each scenario defines safe, non-destructive test probes, expected secure behaviors,
vulnerability indicators, CWE/OWASP mappings, and defensive remediation guidance.
"""

SCENARIOS = [
    {
        "id": "auth-boundary",
        "name": "Authentication Boundary & Token Validation",
        "category": "Authentication",
        "description": (
            "Evaluates whether sensitive administrative or user configuration endpoints "
            "enforce strict authentication boundaries. Probes target endpoints with missing, "
            "empty, and invalid bearer tokens to verify that unauthorized requests are rejected."
        ),
        "severity_default": "HIGH",
        "cwe_id": "CWE-287",
        "owasp_category": "A07:2021-Identification and Authentication Failures",
        "target_endpoint_vulnerable": "/api/vulnerable/user/settings",
        "target_endpoint_remediated": "/api/remediated/user/settings",
        "remediation_guidance": (
            "Enforce mandatory authentication middleware or dependency injection (e.g., FastAPI's "
            "`Security` or `Depends(oauth2_scheme)`). Ensure any request lacking a valid, unexpired "
            "JWT/Bearer token is immediately rejected with HTTP 401 Unauthorized and WWW-Authenticate header."
        ),
        "steps": [
            {
                "step_number": 1,
                "name": "Probe with missing Authorization header",
                "method": "GET",
                "headers": {},
                "body": None,
                "expected_status": 401,
                "expected_behavior": "Target must reject unauthenticated request with HTTP 401 Unauthorized.",
                "vulnerability_condition": "Status == 200 with sensitive configuration or user attributes returned.",
                "remediation_note": "Apply authentication dependency to the router."
            },
            {
                "step_number": 2,
                "name": "Probe with malformed Bearer token",
                "method": "GET",
                "headers": {"Authorization": "Bearer null"},
                "body": None,
                "expected_status": 401,
                "expected_behavior": "Target must reject malformed token with HTTP 401 Unauthorized.",
                "vulnerability_condition": "Status == 200 or unhandled server crash (HTTP 500).",
                "remediation_note": "Ensure JWT/token parser catches decoding exceptions and raises HTTP 401."
            },
            {
                "step_number": 3,
                "name": "Probe with arbitrary invalid token",
                "method": "GET",
                "headers": {"Authorization": "Bearer forged_or_expired_token_xyz"},
                "body": None,
                "expected_status": 401,
                "expected_behavior": "Target must reject untrusted token with HTTP 401 Unauthorized.",
                "vulnerability_condition": "Status == 200 granting access to resource.",
                "remediation_note": "Validate cryptographic signature and expiration claims on all tokens."
            }
        ]
    },
    {
        "id": "input-validation",
        "name": "Input Boundary & Type Validation",
        "category": "Input Validation",
        "description": (
            "Tests application resilience against boundary violations, negative values, and "
            "malformed data types. Verifies whether endpoints enforce strict schema validation "
            "or fail unsafely by leaking stack traces and permitting logic bypasses."
        ),
        "severity_default": "MEDIUM",
        "cwe_id": "CWE-20",
        "owasp_category": "A03:2021-Injection & Validation Failures",
        "target_endpoint_vulnerable": "/api/vulnerable/calculate-discount",
        "target_endpoint_remediated": "/api/remediated/calculate-discount",
        "remediation_guidance": (
            "Utilize strict schema validation libraries (such as Pydantic) to enforce bounds "
            "(e.g., `Field(gt=0)`). Handle validation exceptions centrally to return clean HTTP 422 "
            "or 400 error codes without leaking internal stack traces or Python error details."
        ),
        "steps": [
            {
                "step_number": 1,
                "name": "Submit negative quantity value",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": {"price": 100.0, "quantity": -5},
                "expected_status": 422,
                "expected_behavior": "Target must reject negative quantity with HTTP 422 Unprocessable Entity.",
                "vulnerability_condition": "Status == 200 resulting in business logic calculation anomaly (negative total).",
                "remediation_note": "Enforce `Field(gt=0)` on quantity in the Pydantic request model."
            },
            {
                "step_number": 2,
                "name": "Submit zero quantity (division boundary test)",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": {"price": 100.0, "quantity": 0},
                "expected_status": 422,
                "expected_behavior": "Target must reject zero quantity or handle calculation safely.",
                "vulnerability_condition": "Status == 500 Internal Server Error leaking ZeroDivisionError trace.",
                "remediation_note": "Guard against division by zero and enforce minimum quantity >= 1."
            },
            {
                "step_number": 3,
                "name": "Submit invalid string data type for numeric field",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": {"price": 100.0, "quantity": "invalid_number_string"},
                "expected_status": 422,
                "expected_behavior": "Target must reject non-numeric type with HTTP 422 schema error.",
                "vulnerability_condition": "Status == 500 unhandled TypeError with debug stack trace.",
                "remediation_note": "Do not use raw dictionary parsing; use strongly typed Pydantic models."
            }
        ]
    },
    {
        "id": "session-security",
        "name": "Session Security & Cookie Attribute Hardening",
        "category": "Session Management",
        "description": (
            "Audits cookie attributes established during session generation. Checks for defensive "
            "flags including HttpOnly (prevents XSS cookie theft), SameSite (prevents CSRF), "
            "and Secure (requires encrypted transport)."
        ),
        "severity_default": "MEDIUM",
        "cwe_id": "CWE-614",
        "owasp_category": "A07:2021-Identification and Authentication Failures",
        "target_endpoint_vulnerable": "/api/vulnerable/auth/session",
        "target_endpoint_remediated": "/api/remediated/auth/session",
        "remediation_guidance": (
            "Configure all session and authentication cookies with `httponly=True`, `samesite='lax'` "
            "or `'strict'`, and `secure=True`. Generate session identifiers using cryptographically secure "
            "random generators (e.g. `secrets.token_urlsafe()` or UUID4)."
        ),
        "steps": [
            {
                "step_number": 1,
                "name": "Inspect session cookie flags (HttpOnly & SameSite)",
                "method": "POST",
                "headers": {},
                "body": None,
                "expected_status": 200,
                "expected_behavior": "Response Set-Cookie header must include HttpOnly and SameSite=Lax/Strict.",
                "vulnerability_condition": "Cookie is missing HttpOnly flag, allowing JavaScript document.cookie access.",
                "remediation_note": "Set `httponly=True` and `samesite='lax'` when calling `response.set_cookie()`."
            }
        ]
    },
    {
        "id": "rate-limiting",
        "name": "Rate-Limit Threshold & Brute-Force Resilience",
        "category": "Rate Limiting",
        "description": (
            "Sends rapid consecutive requests to an authentication or API probe endpoint to verify "
            "whether the application enforces interaction frequency limits to mitigate brute-force "
            "and resource exhaustion attacks."
        ),
        "severity_default": "HIGH",
        "cwe_id": "CWE-799",
        "owasp_category": "A04:2021-Insecure Design",
        "target_endpoint_vulnerable": "/api/vulnerable/auth/login-probe",
        "target_endpoint_remediated": "/api/remediated/auth/login-probe",
        "remediation_guidance": (
            "Implement sliding-window or token-bucket rate limiting based on client IP or user ID. "
            "Return HTTP 429 Too Many Requests with a `Retry-After` header when rate limits are exceeded."
        ),
        "steps": [
            {
                "step_number": 1,
                "name": "Transmit rapid burst of 7 consecutive requests",
                "method": "POST",
                "headers": {},
                "body": None,
                "burst_count": 7,
                "expected_status": 429,
                "expected_behavior": "Target must enforce rate limiting and return HTTP 429 after exceeding limit.",
                "vulnerability_condition": "All burst requests succeed (HTTP 200) without any rate limiting or throttling.",
                "remediation_note": "Integrate rate-limiting middleware (e.g., slowapi) to throttle rapid requests."
            }
        ]
    },
    {
        "id": "api-authorization",
        "name": "Broken Object Level Authorization (BOLA / IDOR)",
        "category": "Access Control",
        "description": (
            "Assesses object-level access control boundaries. Tests whether an authenticated "
            "user (Alice) can access private, restricted documents owned by another user (Bob) "
            "by simply manipulating the resource ID parameter."
        ),
        "severity_default": "CRITICAL",
        "cwe_id": "CWE-639",
        "owasp_category": "A01:2021-Broken Access Control",
        "target_endpoint_vulnerable": "/api/vulnerable/documents/202",
        "target_endpoint_remediated": "/api/remediated/documents/202",
        "remediation_guidance": (
            "Enforce authorization checks at the data layer for every object retrieval. Check "
            "whether `current_user.id == resource.owner_id` (or user possesses explicit tenant role). "
            "Return HTTP 403 Forbidden or 404 Not Found if access is not permitted."
        ),
        "steps": [
            {
                "step_number": 1,
                "name": "Attempt reading User Bob's confidential document as User Alice",
                "method": "GET",
                "headers": {"Authorization": "Bearer alice_token"},
                "body": None,
                "expected_status": 403,
                "expected_behavior": "Target must deny unauthorized access to Bob's document with HTTP 403 Forbidden.",
                "vulnerability_condition": "Target returns HTTP 200 leaking Bob's private document data.",
                "remediation_note": "Validate resource ownership in the controller before returning document content."
            }
        ]
    }
]
