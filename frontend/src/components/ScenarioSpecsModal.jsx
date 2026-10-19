import React, { useState, useEffect } from "react";
import { getScenarioDetail } from "../api";

export default function ScenarioSpecsModal({ scenarioId, onClose, onLaunch }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!scenarioId) return;
    setLoading(true);
    getScenarioDetail(scenarioId)
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [scenarioId]);

  if (!scenarioId) return null;

  return (
    <div style={{
      position: "fixed",
      top: 0, left: 0, right: 0, bottom: 0,
      background: "rgba(0,0,0,0.8)",
      backdropFilter: "blur(6px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 100,
      padding: "1.5rem"
    }}>
      <div className="glass-panel" style={{
        width: "100%",
        maxWidth: "750px",
        maxHeight: "85vh",
        background: "var(--bg-secondary)",
        borderRadius: "12px",
        border: "1px solid var(--border-glow)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden"
      }}>
        {/* Header */}
        <div style={{
          padding: "1rem 1.5rem",
          borderBottom: "1px solid var(--border-subtle)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: "var(--bg-input)"
        }}>
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f8fafc" }}>
              {data?.name || "Scenario Specifications"}
            </h3>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              ID: <code>{scenarioId}</code>
            </span>
          </div>
          <button onClick={onClose} className="btn btn-secondary btn-sm">✕</button>
        </div>

        {/* Content */}
        <div style={{ padding: "1.5rem", overflowY: "auto", flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
              Loading specifications...
            </div>
          ) : data ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <span className="badge badge-cyan">{data.category}</span>
                <span className="badge badge-purple">{data.cwe_id}</span>
                <span className="badge badge-crimson">{data.owasp_category}</span>
                <span className="badge badge-amber">Default Severity: {data.severity_default}</span>
              </div>

              <div>
                <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                  Description
                </h4>
                <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "0.3rem", lineHeight: "1.5" }}>
                  {data.description}
                </p>
              </div>

              <div>
                <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, marginBottom: "0.5rem" }}>
                  Predefined Safe Test Probes ({data.steps?.length || 0} Steps)
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {data.steps?.map((step, idx) => (
                    <div key={idx} style={{
                      background: "var(--bg-input)",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "6px",
                      padding: "0.75rem 1rem"
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                        <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "#f8fafc" }}>
                          Step {step.step_number}: {step.name}
                        </span>
                        <span className="badge badge-cyan" style={{ fontSize: "0.7rem" }}>
                          {step.method} (Expected: {step.expected_status})
                        </span>
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                        {step.expected_behavior}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{
                background: "rgba(6, 182, 212, 0.05)",
                border: "1px solid rgba(6, 182, 212, 0.25)",
                borderRadius: "8px",
                padding: "1rem"
              }}>
                <h4 style={{ fontSize: "0.85rem", color: "var(--cyan-glow)", fontWeight: 700, marginBottom: "0.3rem" }}>
                  Remediation Summary
                </h4>
                <p style={{ fontSize: "0.825rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                  {data.remediation_guidance}
                </p>
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div style={{
          padding: "0.85rem 1.5rem",
          borderTop: "1px solid var(--border-subtle)",
          background: "var(--bg-input)",
          display: "flex",
          justifyContent: "flex-end",
          gap: "0.75rem"
        }}>
          <button onClick={onClose} className="btn btn-secondary btn-sm">Close</button>
          <button
            onClick={() => {
              onClose();
              onLaunch(scenarioId);
            }}
            className="btn btn-primary btn-sm"
          >
            ⚡ Run Simulation
          </button>
        </div>
      </div>
    </div>
  );
}
