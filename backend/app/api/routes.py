"""
API Routes for Black-Box Attack Simulator Backend.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import httpx

from app.db.session import get_db
from app.db.models import Scenario, SimulationRun, TestStepResult, SecurityReport
from app.core.safety import validate_target_url, SecurityViolationError
from app.engine.runner import execute_simulation
from app.analyzer.evaluator import evaluate_simulation_results
from app.reports.generator import generate_security_report

router = APIRouter()


class SimulationRequest(BaseModel):
    scenario_id: str
    target_url: str = "http://localhost:8001"
    target_mode: str = "vulnerable"  # "vulnerable" or "remediated"


@router.get("/health")
def backend_health():
    """Returns backend system status."""
    return {
        "status": "online",
        "service": "Black-Box Attack Simulator Engine",
        "version": "1.0.0",
        "sandbox_enforced": True
    }


@router.get("/target/health")
async def target_health_check(url: str = Query("http://localhost:8001")):
    """
    Checks if the local training target sandbox is reachable.
    Strictly validates target URL to ensure it never scans external hosts.
    """
    try:
        validated_url = validate_target_url(url)
    except SecurityViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Safety Guardrail Blocked Target: {str(e)}"
        )

    health_url = validated_url.rstrip("/") + "/health"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(health_url)
            if resp.status_code == 200:
                return {
                    "reachable": True,
                    "target_url": validated_url,
                    "response": resp.json()
                }
            return {
                "reachable": False,
                "target_url": validated_url,
                "status_code": resp.status_code,
                "error": "Target returned non-200 status code."
            }
    except Exception as e:
        return {
            "reachable": False,
            "target_url": validated_url,
            "error": f"Target service unreachable at {health_url}: {str(e)}"
        }


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    """Lists all available educational security scenarios."""
    scenarios = db.query(Scenario).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "description": s.description,
            "severity_default": s.severity_default,
            "cwe_id": s.cwe_id,
            "owasp_category": s.owasp_category,
            "target_endpoint_vulnerable": s.target_endpoint_vulnerable,
            "target_endpoint_remediated": s.target_endpoint_remediated,
            "remediation_guidance": s.remediation_guidance,
            "steps_count": len(s.steps_definition) if s.steps_definition else 0
        }
        for s in scenarios
    ]


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Retrieves a single scenario by ID with its predefined steps."""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return {
        "id": scenario.id,
        "name": scenario.name,
        "category": scenario.category,
        "description": scenario.description,
        "severity_default": scenario.severity_default,
        "cwe_id": scenario.cwe_id,
        "owasp_category": scenario.owasp_category,
        "target_endpoint_vulnerable": scenario.target_endpoint_vulnerable,
        "target_endpoint_remediated": scenario.target_endpoint_remediated,
        "remediation_guidance": scenario.remediation_guidance,
        "steps": scenario.steps_definition
    }


@router.post("/simulations/run")
async def run_simulation(req: SimulationRequest, db: Session = Depends(get_db)):
    """
    Executes a predefined educational security simulation against the local sandbox.
    Enforces strict safety guardrails.
    """
    # 1. Look up scenario
    scenario = db.query(Scenario).filter(Scenario.id == req.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found.")

    # 2. Safety validation
    try:
        validated_target = validate_target_url(req.target_url)
    except SecurityViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Safety Guardrail Blocked Target: {str(e)}"
        )

    # 3. Create SimulationRun record
    run = SimulationRun(
        scenario_id=scenario.id,
        target_url=validated_target,
        status="RUNNING"
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # 4. Prepare scenario dictionary for runner
    scen_dict = {
        "id": scenario.id,
        "name": scenario.name,
        "category": scenario.category,
        "severity_default": scenario.severity_default,
        "cwe_id": scenario.cwe_id,
        "owasp_category": scenario.owasp_category,
        "target_endpoint_vulnerable": scenario.target_endpoint_vulnerable,
        "target_endpoint_remediated": scenario.target_endpoint_remediated,
        "remediation_guidance": scenario.remediation_guidance,
        "steps": scenario.steps_definition
    }

    # 5. Execute simulation
    step_results, duration_ms, sim_status = await execute_simulation(
        scen_dict,
        validated_target,
        target_mode=req.target_mode
    )

    # 6. Evaluate results
    verdict, severity, summary = evaluate_simulation_results(
        scen_dict,
        step_results,
        sim_status
    )

    # 7. Update run record
    run.status = sim_status
    run.overall_verdict = verdict
    run.calculated_severity = severity
    run.duration_ms = duration_ms
    run.summary = summary

    # 8. Persist step results
    for s in step_results:
        step_rec = TestStepResult(
            run_id=run.id,
            step_number=s["step_number"],
            step_name=s["step_name"],
            expected_behavior=s["expected_behavior"],
            observed_behavior=s["observed_behavior"],
            verdict=s["verdict"],
            http_status_code=s.get("http_status_code"),
            request_dump=s.get("request_dump"),
            response_dump=s.get("response_dump"),
            remediation_note=s.get("remediation_note")
        )
        db.add(step_rec)

    # 9. Generate security report
    report_data = generate_security_report(
        run_id=run.id,
        scenario=scen_dict,
        target_url=validated_target,
        verdict=verdict,
        severity=severity,
        duration_ms=duration_ms,
        step_results=step_results,
        summary=summary
    )

    report_rec = SecurityReport(
        run_id=run.id,
        title=report_data["title"],
        format=report_data["format"],
        content_markdown=report_data["content_markdown"],
        content_json=report_data["content_json"]
    )
    db.add(report_rec)
    db.commit()
    db.refresh(run)

    return {
        "run_id": run.id,
        "scenario_id": run.scenario_id,
        "scenario_name": scenario.name,
        "target_url": run.target_url,
        "target_mode": req.target_mode,
        "status": run.status,
        "overall_verdict": run.overall_verdict,
        "calculated_severity": run.calculated_severity,
        "duration_ms": run.duration_ms,
        "summary": run.summary,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "step_results": step_results,
        "remediation_guidance": scenario.remediation_guidance
    }


@router.get("/simulations/history")
def get_simulation_history(db: Session = Depends(get_db)):
    """Retrieves all past simulation runs sorted chronologically descending."""
    runs = db.query(SimulationRun).order_by(SimulationRun.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "scenario_id": r.scenario_id,
            "scenario_name": r.scenario.name if r.scenario else r.scenario_id,
            "category": r.scenario.category if r.scenario else "Unknown",
            "target_url": r.target_url,
            "status": r.status,
            "overall_verdict": r.overall_verdict,
            "calculated_severity": r.calculated_severity,
            "duration_ms": r.duration_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "summary": r.summary
        }
        for r in runs
    ]


@router.get("/simulations/{run_id}")
def get_simulation_detail(run_id: str, db: Session = Depends(get_db)):
    """Retrieves detailed results for a single simulation run."""
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Simulation run '{run_id}' not found.")

    steps = [
        {
            "step_number": s.step_number,
            "step_name": s.step_name,
            "expected_behavior": s.expected_behavior,
            "observed_behavior": s.observed_behavior,
            "verdict": s.verdict,
            "http_status_code": s.http_status_code,
            "request_dump": s.request_dump,
            "response_dump": s.response_dump,
            "remediation_note": s.remediation_note
        }
        for s in run.step_results
    ]

    report = run.report
    return {
        "id": run.id,
        "scenario_id": run.scenario_id,
        "scenario_name": run.scenario.name if run.scenario else run.scenario_id,
        "cwe_id": run.scenario.cwe_id if run.scenario else None,
        "owasp_category": run.scenario.owasp_category if run.scenario else None,
        "target_url": run.target_url,
        "status": run.status,
        "overall_verdict": run.overall_verdict,
        "calculated_severity": run.calculated_severity,
        "duration_ms": run.duration_ms,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "summary": run.summary,
        "step_results": steps,
        "remediation_guidance": run.scenario.remediation_guidance if run.scenario else None,
        "report_id": report.id if report else None
    }


@router.get("/reports/{run_id}")
def get_report(run_id: str, db: Session = Depends(get_db)):
    """Retrieves the security assessment report for a run."""
    report = db.query(SecurityReport).filter(SecurityReport.run_id == run_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report for run '{run_id}' not found.")
    return {
        "id": report.id,
        "run_id": report.run_id,
        "title": report.title,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        "format": report.format,
        "content_markdown": report.content_markdown,
        "content_json": report.content_json
    }


@router.get("/reports/{run_id}/markdown")
def download_markdown_report(run_id: str, db: Session = Depends(get_db)):
    """Downloads the security assessment report as raw Markdown."""
    report = db.query(SecurityReport).filter(SecurityReport.run_id == run_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report for run '{run_id}' not found.")

    return Response(
        content=report.content_markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=assessment_{run_id}.md"}
    )
