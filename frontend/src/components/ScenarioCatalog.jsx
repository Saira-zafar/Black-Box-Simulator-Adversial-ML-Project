import React, { useState } from "react";

export default function ScenarioCatalog({ scenarios, onLaunchSimulation }) {
  const [selectedId, setSelectedId] = useState(scenarios[0]?.id || "auth-boundary");

  const selectedScenario = scenarios.find(s => s.id === selectedId) || scenarios[0];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div>
        <h2 style={{ fontSize: "1.3rem", fontWeight: 700 }}>Predefined Scenario Catalog</h2>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
          Standardized educational test cases mapped to the OWASP Top 10 and MITRE CWE taxonomies.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: "1.5rem" }}>
        {/* Sidebar Scenario List */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {scenarios.map(scen => (
            <div
              key={scen.id}
              onClick={() => setSelectedId(scen.id)}
              style={{
                background: selectedId === scen.id ? "rgba(6, 182, 212, 0.15)" : "var(--bg-card)",
                border: "1px solid",
                borderColor: selectedId === scen.id ? "var(--cyan)" : "var(--border-subtle)",
                borderRadius: "8px",
                padding: "0.85rem 1rem",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                <span className="badge badge-cyan" style={{ fontSize: "0.7rem" }}>{scen.category}</span>
                <span className="badge badge-purple" style={{ fontSize: "0.7rem" }}>{scen.cwe_id}</span>
              </div>
              <div style={{ fontWeight: 700, fontSize: "0.9rem", color: selectedId === scen.id ? "var(--cyan-glow)" : "#f8fafc" }}>
                {scen.name}
              </div>
            </div>
          ))}
        </div>

        {/* Selected Scenario Drilldown */}
        {selectedScenario && (
          <div className="glass-panel" style={{ padding: "1.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
              <div>
                <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
                  <span className="badge badge-cyan">{selectedScenario.category}</span>
                  <span className="badge badge-purple">{selectedScenario.cwe_id}</span>
                  <span className="badge badge-crimson">{selectedScenario.owasp_category}</span>
                </div>
                <h3 style={{ fontSize: "1.4rem", fontWeight: 800, color: "#f8fafc" }}>
                  {selectedScenario.name}
                </h3>
              </div>
              <button
                id="catalog-launch-btn"
                onClick={() => onLaunchSimulation(selectedScenario.id)}
                className="btn btn-primary"
              >
                ⚡ Execute Scenario
              </button>
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
              <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "0.5rem", fontWeight: 700 }}>
                Scenario Overview & Educational Context
              </h4>
              <p style={{ fontSize: "0.925rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {selectedScenario.description}
              </p>
            </div>

            <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
              <div style={{ background: "var(--bg-input)", padding: "1rem", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: "0.75rem", color: "#f87171", fontWeight: 700, marginBottom: "0.25rem" }}>
                  VULNERABLE TARGET ENDPOINT
                </div>
                <code style={{ fontSize: "0.85rem", color: "#f87171" }}>
                  {selectedScenario.target_endpoint_vulnerable}
                </code>
                <p style={{ fontSize: "0.775rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
                  Intentionally misconfigured endpoint for discovering and analyzing flaws.
                </p>
              </div>

              <div style={{ background: "var(--bg-input)", padding: "1rem", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: "0.75rem", color: "#34d399", fontWeight: 700, marginBottom: "0.25rem" }}>
                  REMEDIATED SECURE ENDPOINT
                </div>
                <code style={{ fontSize: "0.85rem", color: "#34d399" }}>
                  {selectedScenario.target_endpoint_remediated}
                </code>
                <p style={{ fontSize: "0.775rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
                  Hardened counterpart with defensive controls implemented.
                </p>
              </div>
            </div>

            <div style={{
              background: "rgba(6, 182, 212, 0.05)",
              border: "1px solid rgba(6, 182, 212, 0.2)",
              borderRadius: "8px",
              padding: "1.25rem"
            }}>
              <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--cyan-glow)", marginBottom: "0.5rem", fontWeight: 700 }}>
                🛡️ Defensive Remediation Specification
              </h4>
              <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                {selectedScenario.remediation_guidance}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
