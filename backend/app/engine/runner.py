"""
Safe Simulation Engine Runner.

ENFORCEMENT:
Every URL passed to this runner is validated against the Safety Guardrails
(backend.app.core.safety) before any socket or HTTP connection is initiated.
"""

import httpx
import time
from typing import Dict, Any, List, Tuple
from urllib.parse import urljoin

from app.core.safety import validate_target_url, SecurityViolationError


async def execute_simulation(
    scenario: Dict[str, Any],
    target_base_url: str,
    target_mode: str = "vulnerable"  # "vulnerable" or "remediated"
) -> Tuple[List[Dict[str, Any]], float, str]:
    """
    Executes a predefined educational security scenario against the local training target.
    
    Returns:
        (step_results, duration_ms, status)
    """
    start_time = time.perf_counter()
    step_results = []

    # Choose endpoint path based on mode
    if target_mode == "remediated":
        endpoint_path = scenario.get("target_endpoint_remediated")
    else:
        endpoint_path = scenario.get("target_endpoint_vulnerable")

    full_target_url = urljoin(target_base_url.rstrip("/") + "/", endpoint_path.lstrip("/"))

    # STRICT SAFETY VALIDATION
    try:
        validate_target_url(full_target_url)
    except SecurityViolationError as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        step_results.append({
            "step_number": 1,
            "step_name": "Safety Guardrail Check",
            "expected_behavior": "Target must strictly be an authorized local sandbox.",
            "observed_behavior": f"Blocked by safety guardrail: {str(e)}",
            "verdict": "FAIL",
            "http_status_code": None,
            "request_dump": {"url": full_target_url},
            "response_dump": {"error": "SAFETY_BLOCKED"},
            "remediation_note": "Ensure target URL is localhost or local docker training container."
        })
        return step_results, duration_ms, "SAFETY_BLOCKED"

    steps = scenario.get("steps", [])

    async with httpx.AsyncClient(timeout=5.0) as client:
        for step in steps:
            step_num = step.get("step_number", len(step_results) + 1)
            step_name = step.get("name", f"Step {step_num}")
            method = step.get("method", "GET").upper()
            headers = step.get("headers", {}).copy()
            body = step.get("body")
            expected_status = step.get("expected_status")
            burst_count = step.get("burst_count", 1)

            req_dump = {
                "method": method,
                "url": full_target_url,
                "headers": {k: v for k, v in headers.items() if k.lower() != "authorization"} if "Authorization" in headers else headers,
                "body": body
            }

            try:
                # Handle burst rate-limiting steps
                if burst_count > 1:
                    responses = []
                    for _ in range(burst_count):
                        if method == "POST":
                            res = await client.post(full_target_url, json=body, headers=headers)
                        else:
                            res = await client.get(full_target_url, headers=headers)
                        responses.append(res)

                    status_codes = [r.status_code for r in responses]
                    any_throttled = 429 in status_codes
                    last_res = responses[-1]

                    resp_dump = {
                        "burst_total": burst_count,
                        "status_codes_received": status_codes,
                        "last_response_body": last_res.text[:300]
                    }

                    if any_throttled:
                        verdict = "PASS"
                        observed = (
                            f"Target enforced rate limiting. Burst of {burst_count} requests resulted in "
                            f"HTTP 429 Too Many Requests (Status codes: {status_codes})."
                        )
                    else:
                        verdict = "FAIL"
                        observed = (
                            f"VULNERABILITY DETECTED: Target accepted all {burst_count} requests without throttling "
                            f"(Status codes: {status_codes}). No HTTP 429 returned."
                        )

                    step_results.append({
                        "step_number": step_num,
                        "step_name": step_name,
                        "expected_behavior": step.get("expected_behavior"),
                        "observed_behavior": observed,
                        "verdict": verdict,
                        "http_status_code": last_res.status_code,
                        "request_dump": req_dump,
                        "response_dump": resp_dump,
                        "remediation_note": step.get("remediation_note")
                    })
                    continue

                # Normal single-step execution
                if method == "POST":
                    response = await client.post(full_target_url, json=body, headers=headers)
                elif method == "GET":
                    response = await client.get(full_target_url, headers=headers)
                else:
                    response = await client.request(method, full_target_url, json=body, headers=headers)

                # Special check for session cookie security
                if scenario.get("id") == "session-security":
                    cookie_header = response.headers.get("set-cookie", "")
                    has_httponly = "httponly" in cookie_header.lower()
                    has_samesite = "samesite" in cookie_header.lower()

                    resp_dump = {
                        "status_code": response.status_code,
                        "set_cookie": cookie_header,
                        "body_excerpt": response.text[:200]
                    }

                    if has_httponly and has_samesite:
                        verdict = "PASS"
                        observed = (
                            f"Secure session configuration observed. Set-Cookie contains HttpOnly and SameSite flags: {cookie_header}"
                        )
                    else:
                        verdict = "FAIL"
                        missing_flags = []
                        if not has_httponly:
                            missing_flags.append("HttpOnly (XSS risk)")
                        if not has_samesite:
                            missing_flags.append("SameSite (CSRF risk)")
                        observed = (
                            f"VULNERABILITY DETECTED: Session cookie missing defensive flags: {', '.join(missing_flags)}. "
                            f"Raw Set-Cookie: '{cookie_header}'"
                        )

                    step_results.append({
                        "step_number": step_num,
                        "step_name": step_name,
                        "expected_behavior": step.get("expected_behavior"),
                        "observed_behavior": observed,
                        "verdict": verdict,
                        "http_status_code": response.status_code,
                        "request_dump": req_dump,
                        "response_dump": resp_dump,
                        "remediation_note": step.get("remediation_note")
                    })
                    continue

                # Standard response evaluation
                resp_dump = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body_excerpt": response.text[:300]
                }

                if response.status_code == expected_status:
                    verdict = "PASS"
                    observed = f"Target returned expected status HTTP {response.status_code}. Access properly controlled/handled."
                else:
                    verdict = "FAIL"
                    observed = (
                        f"VULNERABILITY DETECTED: Expected HTTP {expected_status}, but target returned "
                        f"HTTP {response.status_code}. Excerpt: {response.text[:120]}"
                    )

                step_results.append({
                    "step_number": step_num,
                    "step_name": step_name,
                    "expected_behavior": step.get("expected_behavior"),
                    "observed_behavior": observed,
                    "verdict": verdict,
                    "http_status_code": response.status_code,
                    "request_dump": req_dump,
                    "response_dump": resp_dump,
                    "remediation_note": step.get("remediation_note")
                })

            except httpx.RequestError as exc:
                step_results.append({
                    "step_number": step_num,
                    "step_name": step_name,
                    "expected_behavior": step.get("expected_behavior"),
                    "observed_behavior": f"Connection error contacting target: {str(exc)}. Is the training service running on this port?",
                    "verdict": "FAIL",
                    "http_status_code": None,
                    "request_dump": req_dump,
                    "response_dump": {"error": str(exc)},
                    "remediation_note": "Verify that the local training target service is running on the specified port."
                })

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return step_results, duration_ms, "COMPLETED"
