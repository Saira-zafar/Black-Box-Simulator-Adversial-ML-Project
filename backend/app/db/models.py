"""
SQLAlchemy ORM Models for Black-Box Attack Simulator.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.session import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    severity_default = Column(String(16), nullable=False)  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    cwe_id = Column(String(32), nullable=False)
    owasp_category = Column(String(64), nullable=False)
    target_endpoint_vulnerable = Column(String(128), nullable=False)
    target_endpoint_remediated = Column(String(128), nullable=False)
    remediation_guidance = Column(Text, nullable=False)
    steps_definition = Column(JSON, nullable=False)

    runs = relationship("SimulationRun", back_populates="scenario")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id = Column(String(64), ForeignKey("scenarios.id"), nullable=False)
    target_url = Column(String(256), nullable=False)
    status = Column(String(32), default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, SAFETY_BLOCKED
    overall_verdict = Column(String(32), default="PENDING")  # SECURE, VULNERABLE, ERROR
    calculated_severity = Column(String(16), default="INFO")
    duration_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    summary = Column(Text, nullable=True)

    scenario = relationship("Scenario", back_populates="runs")
    step_results = relationship("TestStepResult", back_populates="run", cascade="all, delete-orphan")
    report = relationship("SecurityReport", back_populates="run", uselist=False, cascade="all, delete-orphan")


class TestStepResult(Base):
    __tablename__ = "test_step_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("simulation_runs.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(128), nullable=False)
    expected_behavior = Column(Text, nullable=False)
    observed_behavior = Column(Text, nullable=False)
    verdict = Column(String(16), nullable=False)  # PASS, FAIL
    http_status_code = Column(Integer, nullable=True)
    request_dump = Column(JSON, nullable=True)
    response_dump = Column(JSON, nullable=True)
    remediation_note = Column(Text, nullable=True)

    run = relationship("SimulationRun", back_populates="step_results")


class SecurityReport(Base):
    __tablename__ = "security_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("simulation_runs.id"), nullable=False)
    title = Column(String(256), nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    format = Column(String(16), default="markdown")
    content_markdown = Column(Text, nullable=False)
    content_json = Column(JSON, nullable=True)

    run = relationship("SimulationRun", back_populates="report")
