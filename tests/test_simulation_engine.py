import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.analyzer.evaluator import evaluate_simulation_results
from app.reports.generator import generate_security_report
from app.engine.scenarios_data import SCENARIOS


def test_evaluator_vulnerable_verdict():
    scenario = SCENARIOS[0]
    step_results = [
        {
            "step_number": 1,
            "step_name": "Test Step 1",
            "expected_behavior": "401 Unauthorized",
            "observed_behavior": "200 OK returned",
            "verdict": "FAIL",
            "http_status_code": 200,
            "request_dump": {},
            "response_dump": {},
            "remediation_note": "Add auth check"
        }
    ]
    verdict, severity, summary = evaluate_simulation_results(scenario, step_results, "COMPLETED")
    assert verdict == "VULNERABLE"
    assert severity == "HIGH"
    assert "VULNERABILITY CONFIRMED" in summary


def test_evaluator_secure_verdict():
    scenario = SCENARIOS[0]
    step_results = [
        {
            "step_number": 1,
            "step_name": "Test Step 1",
            "expected_behavior": "401 Unauthorized",
            "observed_behavior": "401 Unauthorized returned",
            "verdict": "PASS",
            "http_status_code": 401,
            "request_dump": {},
            "response_dump": {},
            "remediation_note": "Add auth check"
        }
    ]
    verdict, severity, summary = evaluate_simulation_results(scenario, step_results, "COMPLETED")
    assert verdict == "SECURE"
    assert severity == "INFO"
    assert "passed" in summary


def test_report_generator_content():
    scenario = SCENARIOS[0]
    step_results = [
        {
            "step_number": 1,
            "step_name": "Probe with missing Auth header",
            "expected_behavior": "HTTP 401",
            "observed_behavior": "HTTP 200 returned sensitive data",
            "verdict": "FAIL",
            "http_status_code": 200,
            "request_dump": {"url": "http://localhost:8001/api/vulnerable/user/settings"},
            "response_dump": {"user_id": 1},
            "remediation_note": "Apply authentication dependency"
        }
    ]
    report = generate_security_report(
        run_id="test-run-123",
        scenario=scenario,
        target_url="http://localhost:8001",
        verdict="VULNERABLE",
        severity="HIGH",
        duration_ms=45.2,
        step_results=step_results,
        summary="Vulnerability confirmed."
    )

    assert "test-run-123" in report["content_markdown"]
    assert "CWE-287" in report["content_markdown"]
    assert "VULNERABLE" in report["content_markdown"]
    assert report["content_json"]["verdict"] == "VULNERABLE"
    assert report["content_json"]["severity"] == "HIGH"
    assert len(report["content_json"]["step_results"]) == 1
