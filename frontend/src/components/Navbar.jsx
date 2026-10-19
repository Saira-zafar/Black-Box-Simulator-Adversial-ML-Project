import React from "react";

export default function Navbar({
  activeTab,
  setActiveTab,
  targetHealth,
  targetMode,
  setTargetMode,
  onRefreshHealth
}) {
  const isOnline = targetHealth?.reachable;

  return (
    <header style={{
      borderBottom: "1px solid var(--border-subtle)",
      background: "rgba(10, 15, 29, 0.8)",
      backdropFilter: "blur(10px)",
      position: "sticky",
      top: 0,
      zIndex: 50
    }}>
      <div className="container" style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        paddingTop: "0.85rem",
        paddingBottom: "0.85rem"
      }}>
        {/* Logo & Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div style={{
            width: "36px",
            height: "36px",
            borderRadius: "8px",
            background: "linear-gradient(135deg, #06b6d4, #8b5cf6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 0 12px rgba(6, 182, 212, 0.4)",
            fontWeight: "bold",
            fontSize: "1.1rem"
          }}>
            ⚡
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: "1.1rem", letterSpacing: "0.02em", color: "#f8fafc" }}>
              BLACK-BOX <span style={{ color: "var(--cyan-glow)" }}>ATTACK SIMULATOR</span>
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span>🛡️ Local Sandbox Edition</span>
              <span>•</span>
              <span className="badge badge-purple" style={{ fontSize: "0.65rem", padding: "0.1rem 0.4rem" }}>
                🔒 Zero External Access
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <button
            id="nav-dashboard"
            onClick={() => setActiveTab("dashboard")}
            className={`btn btn-sm ${activeTab === "dashboard" ? "btn-primary" : "btn-secondary"}`}
          >
            📊 Dashboard
          </button>
          <button
            id="nav-scenarios"
            onClick={() => setActiveTab("scenarios")}
            className={`btn btn-sm ${activeTab === "scenarios" ? "btn-primary" : "btn-secondary"}`}
          >
            🎯 Scenario Catalog
          </button>
          <button
            id="nav-history"
            onClick={() => setActiveTab("history")}
            className={`btn btn-sm ${activeTab === "history" ? "btn-primary" : "btn-secondary"}`}
          >
            🕒 Test History
          </button>
        </nav>

        {/* Target Status & Target Mode Selector */}
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {/* Target Mode Toggle */}
          <div style={{
            display: "flex",
            alignItems: "center",
            background: "var(--bg-input)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "8px",
            padding: "0.2rem"
          }}>
            <button
              id="mode-toggle-vulnerable"
              onClick={() => setTargetMode("vulnerable")}
              style={{
                padding: "0.25rem 0.6rem",
                fontSize: "0.75rem",
                fontWeight: 600,
                borderRadius: "6px",
                border: "none",
                cursor: "pointer",
                background: targetMode === "vulnerable" ? "var(--crimson-bg)" : "transparent",
                color: targetMode === "vulnerable" ? "#f87171" : "var(--text-muted)",
                transition: "all 0.2s"
              }}
            >
              ⚠️ Vulnerable Target
            </button>
            <button
              id="mode-toggle-remediated"
              onClick={() => setTargetMode("remediated")}
              style={{
                padding: "0.25rem 0.6rem",
                fontSize: "0.75rem",
                fontWeight: 600,
                borderRadius: "6px",
                border: "none",
                cursor: "pointer",
                background: targetMode === "remediated" ? "var(--emerald-bg)" : "transparent",
                color: targetMode === "remediated" ? "#34d399" : "var(--text-muted)",
                transition: "all 0.2s"
              }}
            >
              🛡️ Remediated (Secure)
            </button>
          </div>

          {/* Health Pill */}
          <div
            title="Pinging local training target service at http://localhost:8001"
            onClick={onRefreshHealth}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              background: "var(--bg-input)",
              border: `1px solid ${isOnline ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
              borderRadius: "20px",
              padding: "0.3rem 0.8rem",
              cursor: "pointer",
              fontSize: "0.75rem"
            }}
          >
            <span className={`pulse-dot ${isOnline ? "online" : "offline"}`} />
            <span style={{ color: isOnline ? "#34d399" : "#f87171", fontWeight: 600 }}>
              {isOnline ? "Target Online (:8001)" : "Target Offline"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
