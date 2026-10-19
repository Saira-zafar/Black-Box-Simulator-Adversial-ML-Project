import React from "react";

export default function Dashboard({
  scenarios,
  history,
  targetMode,
  targetHealth,
  onLaunchSimulation,
  onViewScenarioSpecs
}) {
  const totalRuns = history.length;
  const vulnRuns = history.filter(h => h.overall_verdict === "VULNERABLE").length;
  const secureRuns = history.filter(h => h.overall_verdict === "SECURE").length;
  const passRate = totalRuns > 0 ? Math.round((secureRuns / totalRuns) * 100) : 0;

  const getSeverityBadgeClass = (sev) => {
    switch (sev?.toUpperCase()) {
      case "CRITICAL": return "badge-crimson";
      case "HIGH": return "badge-crimson";
      case "MEDIUM": return "badge-amber";
      case "LOW": return "badge-cyan";
      default: return "badge-purple";
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem", paddingBottom: "3rem" }}>
      {/* Safety & Environment Notice */}
      <div className="glass-panel" style={{
        padding: "1.25rem 1.5rem",
        borderLeft: "4px solid var(--cyan)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: "linear-gradient(90deg, rgba(6, 182, 212, 0.08) 0%, rgba(13, 18, 31, 0.8) 100%)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{ fontSize: "1.75rem" }}>🛡️</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "#f8fafc" }}>
              Automated Defensive Sandbox Isolation Active
            </div>
            <div style={{ fontSize: "0.825rem", color: "var(--text-secondary)" }}>
              The simulation engine enforces strict loopback constraints. Outbound requests outside
              <code style={{ color: "var(--cyan)", margin: "0 0.3rem" }}>localhost:8001</code> are blocked at socket level.
            </div>
          </div>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <span className="badge badge-emerald">🔒 Host Guard Active</span>
          <span className="badge badge-purple">RFC1918 / Public IP Filter</span>
        </div>
      </div>

      {/* Metrics Counters */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "1.25rem"
      }}>
        <div className="glass-panel" style={{ padding: "1.25rem" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
            Catalog Scenarios
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--cyan-glow)", marginTop: "0.4rem" }}>
            {scenarios.length}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
            OWASP & CWE Standardized
          </div>
        </div>

        <div className="glass-panel" style={{ padding: "1.25rem" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
            Simulations Executed
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "#f8fafc", marginTop: "0.4rem" }}>
            {totalRuns}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
            Audit log records stored
          </div>
        </div>

        <div className="glass-panel" style={{ padding: "1.25rem" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
            Vulnerabilities Found
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "#f87171", marginTop: "0.4rem" }}>
            {vulnRuns}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
            Identified in vulnerable mode
          </div>
        </div>

        <div className="glass-panel" style={{ padding: "1.25rem" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
            Defensive Pass Rate
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "#34d399", marginTop: "0.4rem" }}>
            {passRate}%
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
            {secureRuns} verified secure tests
          </div>
        </div>
      </div>

      {/* Target Mode Banner */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: targetMode === "vulnerable" ? "rgba(239, 68, 68, 0.08)" : "rgba(16, 185, 129, 0.08)",
        border: `1px solid ${targetMode === "vulnerable" ? "rgba(239, 68, 68, 0.3)" : "rgba(16, 185, 129, 0.3)"}`,
        padding: "0.85rem 1.25rem",
        borderRadius: "10px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{ fontSize: "1.2rem" }}>
            {targetMode === "vulnerable" ? "⚠️" : "🛡️"}
          </span>
          <div>
            <span style={{ fontWeight: 700, color: targetMode === "vulnerable" ? "#f87171" : "#34d399" }}>
              Currently Targeting: {targetMode === "vulnerable" ? "Deliberately Vulnerable Routes" : "Hardened Remediated Routes"}
            </span>
            <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginLeft: "0.75rem" }}>
              {targetMode === "vulnerable"
                ? "Simulations will probe misconfigured routes to detect and demonstrate vulnerabilities."
                : "Simulations will probe hardened routes to verify defensive remediations."}
            </span>
          </div>
        </div>
        <span className={`badge ${targetMode === "vulnerable" ? "badge-crimson" : "badge-emerald"}`}>
          Mode: {targetMode.toUpperCase()}
        </span>
      </div>

      {/* Scenarios Grid */}
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <div>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 700 }}>Educational Security Scenarios</h2>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              Select a standardized simulation to execute safe automated probes against the local training sandbox.
            </p>
          </div>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))",
          gap: "1.5rem"
        }}>
          {scenarios.map((scen) => {
            const endpoint = targetMode === "remediated"
              ? scen.target_endpoint_remediated
              : scen.target_endpoint_vulnerable;

            return (
              <div
                key={scen.id}
                id={`card-${scen.id}`}
                className="glass-panel"
                style={{
                  padding: "1.5rem",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  position: "relative",
                  overflow: "hidden"
                }}
              >
                {/* Header tags */}
                <div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.5rem", marginBottom: "0.75rem" }}>
                    <span className="badge badge-cyan">{scen.category}</span>
                    <div style={{ display: "flex", gap: "0.4rem" }}>
                      <span className="badge badge-purple">{scen.cwe_id}</span>
                      <span className={`badge ${getSeverityBadgeClass(scen.severity_default)}`}>
                        {scen.severity_default}
                      </span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.6rem", color: "#f8fafc" }}>
                    {scen.name}
                  </h3>
                  <p style={{
                    fontSize: "0.825rem",
                    color: "var(--text-secondary)",
                    lineHeight: "1.5",
                    marginBottom: "1rem",
                    display: "-webkit-box",
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden"
                  }}>
                    {scen.description}
                  </p>

                  {/* Endpoint Preview */}
                  <div style={{
                    background: "var(--bg-input)",
                    padding: "0.5rem 0.75rem",
                    borderRadius: "6px",
                    border: "1px solid var(--border-subtle)",
                    fontSize: "0.75rem",
                    fontFamily: "var(--font-mono)",
                    color: "var(--cyan-glow)",
                    marginBottom: "1.25rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem"
                  }}>
                    <span style={{ color: "var(--text-muted)" }}>Target Route:</span>
                    <span>{endpoint}</span>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: "flex", gap: "0.75rem" }}>
                  <button
                    id={`btn-run-${scen.id}`}
                    onClick={() => onLaunchSimulation(scen.id)}
                    className="btn btn-primary"
                    style={{ flex: 1 }}
                  >
                    ⚡ Run Simulation
                  </button>
                  <button
                    id={`btn-spec-${scen.id}`}
                    onClick={() => onViewScenarioSpecs(scen.id)}
                    className="btn btn-secondary"
                  >
                    🔍 Specs
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
