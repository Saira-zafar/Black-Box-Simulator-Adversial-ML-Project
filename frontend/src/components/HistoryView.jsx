import React, { useState } from "react";
import { getReportDownloadUrl } from "../api";

export default function HistoryView({ history, onInspectRun, onViewReport }) {
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const filteredHistory = history.filter(item => {
    if (filter === "VULNERABLE" && item.overall_verdict !== "VULNERABLE") return false;
    if (filter === "SECURE" && item.overall_verdict !== "SECURE") return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        item.scenario_name.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q) ||
        item.target_url.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header & Controls */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 700 }}>Simulation Audit Log & History</h2>
          <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            Review past security assessment runs, verdicts, and forensic evidence.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          {/* Search Box */}
          <input
            id="history-search-input"
            type="text"
            placeholder="Search scenario or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: "var(--bg-input)",
              border: "1px solid var(--border-subtle)",
              color: "#f8fafc",
              padding: "0.4rem 0.8rem",
              borderRadius: "6px",
              fontSize: "0.8rem",
              minWidth: "220px"
            }}
          />

          {/* Filter Pills */}
          <div style={{ display: "flex", background: "var(--bg-input)", padding: "0.2rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
            <button
              onClick={() => setFilter("ALL")}
              style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "4px",
                border: "none",
                background: filter === "ALL" ? "var(--cyan)" : "transparent",
                color: filter === "ALL" ? "#fff" : "var(--text-muted)",
                fontSize: "0.75rem",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              All ({history.length})
            </button>
            <button
              onClick={() => setFilter("VULNERABLE")}
              style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "4px",
                border: "none",
                background: filter === "VULNERABLE" ? "var(--crimson)" : "transparent",
                color: filter === "VULNERABLE" ? "#fff" : "var(--text-muted)",
                fontSize: "0.75rem",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Vulnerable ({history.filter(h => h.overall_verdict === "VULNERABLE").length})
            </button>
            <button
              onClick={() => setFilter("SECURE")}
              style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "4px",
                border: "none",
                background: filter === "SECURE" ? "var(--emerald)" : "transparent",
                color: filter === "SECURE" ? "#fff" : "var(--text-muted)",
                fontSize: "0.75rem",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Secure ({history.filter(h => h.overall_verdict === "SECURE").length})
            </button>
          </div>
        </div>
      </div>

      {/* History Table */}
      <div className="glass-panel" style={{ overflowX: "auto", borderRadius: "10px" }}>
        {filteredHistory.length === 0 ? (
          <div style={{ padding: "3rem", textAlign: "center", color: "var(--text-muted)" }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📭</div>
            <p style={{ fontWeight: 600 }}>No simulation records match your criteria.</p>
            <p style={{ fontSize: "0.8rem", marginTop: "0.25rem" }}>
              Run a security scenario from the Dashboard to record assessments.
            </p>
          </div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{
                background: "rgba(15, 23, 42, 0.9)",
                borderBottom: "1px solid var(--border-subtle)",
                color: "var(--text-muted)",
                textTransform: "uppercase",
                fontSize: "0.75rem",
                letterSpacing: "0.04em"
              }}>
                <th style={{ padding: "0.85rem 1rem" }}>Date / Time</th>
                <th style={{ padding: "0.85rem 1rem" }}>Scenario</th>
                <th style={{ padding: "0.85rem 1rem" }}>Category</th>
                <th style={{ padding: "0.85rem 1rem" }}>Verdict</th>
                <th style={{ padding: "0.85rem 1rem" }}>Severity</th>
                <th style={{ padding: "0.85rem 1rem" }}>Duration</th>
                <th style={{ padding: "0.85rem 1rem", textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.map((item) => {
                const isVuln = item.overall_verdict === "VULNERABLE";
                const dateStr = item.created_at
                  ? new Date(item.created_at).toLocaleString()
                  : "Just now";

                return (
                  <tr
                    key={item.id}
                    style={{
                      borderBottom: "1px solid var(--border-subtle)",
                      transition: "background 0.15s"
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = "rgba(30, 41, 59, 0.4)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                  >
                    <td style={{ padding: "0.85rem 1rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: "0.775rem" }}>
                      {dateStr}
                    </td>
                    <td style={{ padding: "0.85rem 1rem", fontWeight: 600, color: "#f8fafc" }}>
                      {item.scenario_name}
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <span className="badge badge-cyan">{item.category}</span>
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <span className={`badge ${isVuln ? "badge-crimson" : "badge-emerald"}`}>
                        {item.overall_verdict}
                      </span>
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <span className="badge badge-purple">{item.calculated_severity}</span>
                    </td>
                    <td style={{ padding: "0.85rem 1rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                      {item.duration_ms} ms
                    </td>
                    <td style={{ padding: "0.85rem 1rem", textAlign: "right" }}>
                      <div style={{ display: "inline-flex", gap: "0.4rem" }}>
                        <button
                          id={`btn-inspect-${item.id}`}
                          onClick={() => onInspectRun(item.id)}
                          className="btn btn-secondary btn-sm"
                        >
                          🔍 Inspect
                        </button>
                        <a
                          id={`btn-dl-${item.id}`}
                          href={getReportDownloadUrl(item.id)}
                          download
                          className="btn btn-secondary btn-sm"
                          title="Download Markdown Report"
                        >
                          📥 .md
                        </a>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
