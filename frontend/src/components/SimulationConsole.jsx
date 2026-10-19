import React, { useState } from "react";
import { getReportDownloadUrl } from "../api";

export default function SimulationConsole({
  simulationData,
  isRunning,
  onClose,
  onRerun,
  onViewReport
}) {
  const [activeStepTab, setActiveStepTab] = useState(0);

  if (isRunning) {
    return (
      <div className="glass-panel" style={{
        padding: "2rem",
        borderRadius: "14px",
        textAlign: "center",
        border: "1px solid var(--cyan)",
        boxShadow: "0 0 30px rgba(6, 182, 212, 0.2)",
        margin: "1rem 0"
      }}>
        <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>⚡</div>
        <h3 style={{ fontSize: "1.3rem", fontWeight: 700, color: "var(--cyan-glow)" }}>
          Executing Safe Educational Simulation...
        </h3>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "0.5rem" }}>
          Target host strictly constrained to local sandbox. Dispatching predefined compliance test probes...
        </p>
        <div style={{
          height: "6px",
          background: "var(--bg-input)",
          borderRadius: "3px",
          overflow: "hidden",
          margin: "1.5rem auto",
          maxWidth: "400px"
        }}>
          <div style={{
            height: "100%",
            width: "60%",
            background: "linear-gradient(90deg, #06b6d4, #8b5cf6)",
            animation: "pulse-green 1.5s infinite"
          }} />
        </div>
      </div>
    );
  }

  if (!simulationData) return null;

  const isVulnerable = simulationData.overall_verdict === "VULNERABLE";
  const isSecure = simulationData.overall_verdict === "SECURE";
  const steps = simulationData.step_results || [];

  return (
    <div className="glass-panel" style={{
      padding: "2rem",
      borderRadius: "14px",
      border: `1px solid ${isVulnerable ? "rgba(239, 68, 68, 0.5)" : "rgba(16, 185, 129, 0.5)"}`,
      boxShadow: isVulnerable
        ? "0 0 35px rgba(239, 68, 68, 0.15)"
        : "0 0 35px rgba(16, 185, 129, 0.15)",
      margin: "1.5rem 0"
    }}>
      {/* Top Header & Verdict */}
      <div style={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        borderBottom: "1px solid var(--border-subtle)",
        paddingBottom: "1.25rem",
        marginBottom: "1.5rem"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "1.8rem" }}>
              {isVulnerable ? "🚨" : isSecure ? "🛡️" : "⚠️"}
            </span>
            <div>
              <h2 style={{
                fontSize: "1.5rem",
                fontWeight: 800,
                color: isVulnerable ? "#f87171" : isSecure ? "#34d399" : "#fbbf24"
              }}>
                {simulationData.overall_verdict}: {simulationData.scenario_name}
              </h2>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", gap: "0.5rem" }}>
                <span>Target: <code>{simulationData.target_url}</code></span>
                <span>•</span>
                <span>Mode: <code>{simulationData.target_mode}</code></span>
                <span>•</span>
                <span>Execution: <code>{simulationData.duration_ms} ms</code></span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span className={`badge ${isVulnerable ? "badge-crimson" : "badge-emerald"}`} style={{ fontSize: "0.85rem" }}>
            {simulationData.calculated_severity} SEVERITY
          </span>
          <button onClick={onClose} className="btn btn-secondary btn-sm" title="Close Panel">
            ✕
          </button>
        </div>
      </div>

      {/* Assessment Summary Box */}
      <div style={{
        background: "var(--bg-input)",
        padding: "1rem 1.25rem",
        borderRadius: "8px",
        border: "1px solid var(--border-subtle)",
        marginBottom: "1.5rem"
      }}>
        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
          Assessment Conclusion
        </div>
        <p style={{ fontSize: "0.9rem", color: "#f8fafc", marginTop: "0.3rem" }}>
          {simulationData.summary}
        </p>
      </div>

      {/* Interactive Step Inspector */}
      <div style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ fontSize: "1.05rem", fontWeight: 700, marginBottom: "0.75rem", color: "var(--text-primary)" }}>
          Step-by-Step Technical Evidence ({steps.length} checks)
        </h3>

        {/* Step Selector Tabs */}
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", flexWrap: "wrap" }}>
          {steps.map((s, idx) => (
            <button
              key={idx}
              onClick={() => setActiveStepTab(idx)}
              style={{
                padding: "0.4rem 0.8rem",
                borderRadius: "6px",
                border: "1px solid",
                borderColor: activeStepTab === idx ? "var(--cyan)" : "var(--border-subtle)",
                background: activeStepTab === idx ? "rgba(6, 182, 212, 0.15)" : "var(--bg-input)",
                color: activeStepTab === idx ? "var(--cyan-glow)" : "var(--text-secondary)",
                cursor: "pointer",
                fontSize: "0.8rem",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "0.4rem"
              }}
            >
              <span>{s.verdict === "PASS" ? "✅" : "❌"}</span>
              <span>Step {s.step_number}</span>
            </button>
          ))}
        </div>

        {/* Active Step Details */}
        {steps[activeStepTab] && (
          <div style={{
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "10px",
            padding: "1.25rem"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div style={{ fontWeight: 700, fontSize: "1rem", color: "#f8fafc" }}>
                Step {steps[activeStepTab].step_number}: {steps[activeStepTab].step_name}
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <span className={`badge ${steps[activeStepTab].verdict === "PASS" ? "badge-emerald" : "badge-crimson"}`}>
                  {steps[activeStepTab].verdict}
                </span>
                {steps[activeStepTab].http_status_code && (
                  <span className="badge badge-cyan">
                    HTTP {steps[activeStepTab].http_status_code}
                  </span>
                )}
              </div>
            </div>

            {/* Expected vs Observed Comparison */}
            <div className="grid-2" style={{ marginBottom: "1.25rem" }}>
              <div style={{
                background: "rgba(16, 185, 129, 0.05)",
                border: "1px solid rgba(16, 185, 129, 0.2)",
                borderRadius: "8px",
                padding: "0.85rem"
              }}>
                <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#34d399", marginBottom: "0.3rem" }}>
                  EXPECTED RESILIENT BEHAVIOR
                </div>
                <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  {steps[activeStepTab].expected_behavior}
                </div>
              </div>

              <div style={{
                background: steps[activeStepTab].verdict === "FAIL" ? "rgba(239, 68, 68, 0.05)" : "rgba(16, 185, 129, 0.05)",
                border: `1px solid ${steps[activeStepTab].verdict === "FAIL" ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)"}`,
                borderRadius: "8px",
                padding: "0.85rem"
              }}>
                <div style={{
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  color: steps[activeStepTab].verdict === "FAIL" ? "#f87171" : "#34d399",
                  marginBottom: "0.3rem"
                }}>
                  OBSERVED TARGET BEHAVIOR
                </div>
                <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  {steps[activeStepTab].observed_behavior}
                </div>
              </div>
            </div>

            {/* Step Remediation Note */}
            {steps[activeStepTab].remediation_note && (
              <div style={{
                background: "rgba(139, 92, 246, 0.08)",
                border: "1px solid rgba(139, 92, 246, 0.25)",
                borderRadius: "8px",
                padding: "0.75rem 1rem",
                marginBottom: "1rem",
                fontSize: "0.825rem"
              }}>
                <span style={{ fontWeight: 700, color: "#c084fc" }}>💡 Action Item: </span>
                <span style={{ color: "var(--text-secondary)" }}>{steps[activeStepTab].remediation_note}</span>
              </div>
            )}

            {/* Request / Response Dumps */}
            <div className="grid-2">
              <div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.4rem", fontWeight: 600 }}>
                  REQUEST DETAILS
                </div>
                <pre className="code-box" style={{ maxHeight: "150px" }}>
                  {JSON.stringify(steps[activeStepTab].request_dump, null, 2)}
                </pre>
              </div>
              <div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.4rem", fontWeight: 600 }}>
                  RESPONSE DUMP
                </div>
                <pre className="code-box" style={{ maxHeight: "150px" }}>
                  {JSON.stringify(steps[activeStepTab].response_dump, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Defensive Remediation Blueprint */}
      <div style={{
        background: "rgba(6, 182, 212, 0.05)",
        border: "1px solid rgba(6, 182, 212, 0.25)",
        borderRadius: "10px",
        padding: "1.25rem",
        marginBottom: "1.5rem"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
          <span style={{ fontSize: "1.2rem" }}>🛡️</span>
          <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--cyan-glow)" }}>
            Defensive Remediation Blueprint
          </h3>
        </div>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
          {simulationData.remediation_guidance}
        </p>
      </div>

      {/* Action Footer */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            id="btn-view-report"
            onClick={() => onViewReport(simulationData.run_id)}
            className="btn btn-secondary"
          >
            📄 View Full Security Report
          </button>
          <a
            id="btn-download-md"
            href={getReportDownloadUrl(simulationData.run_id)}
            download
            className="btn btn-secondary"
          >
            💾 Download Markdown (.md)
          </a>
        </div>

        <div>
          {isVulnerable && (
            <button
              id="btn-retest-remediated"
              onClick={() => onRerun(simulationData.scenario_id, "remediated")}
              className="btn btn-primary"
            >
              🔄 Test Remediated Endpoint
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
