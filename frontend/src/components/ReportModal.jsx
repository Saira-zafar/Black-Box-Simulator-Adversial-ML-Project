import React, { useState, useEffect } from "react";
import { getReport, getReportDownloadUrl } from "../api";

export default function ReportModal({ runId, onClose }) {
  const [reportData, setReportData] = useState(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!runId) return;
    setLoading(true);
    getReport(runId)
      .then(data => setReportData(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [runId]);

  const handleCopy = () => {
    if (reportData?.content_markdown) {
      navigator.clipboard.writeText(reportData.content_markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!runId) return null;

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "rgba(0, 0, 0, 0.8)",
      backdropFilter: "blur(6px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 100,
      padding: "1.5rem"
    }}>
      <div className="glass-panel" style={{
        width: "100%",
        maxWidth: "900px",
        maxHeight: "90vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--bg-secondary)",
        border: "1px solid var(--border-glow)",
        borderRadius: "12px",
        boxShadow: "0 10px 40px rgba(0,0,0,0.6)",
        overflow: "hidden"
      }}>
        {/* Modal Header */}
        <div style={{
          padding: "1rem 1.5rem",
          borderBottom: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "var(--bg-input)"
        }}>
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f8fafc" }}>
              {reportData?.title || "Security Assessment Report"}
            </h3>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              Run ID: <code>{runId}</code>
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <button
              id="report-copy-btn"
              onClick={handleCopy}
              className="btn btn-secondary btn-sm"
            >
              {copied ? "✅ Copied!" : "📋 Copy Markdown"}
            </button>
            <a
              id="report-download-btn"
              href={getReportDownloadUrl(runId)}
              download
              className="btn btn-primary btn-sm"
            >
              📥 Download .md
            </a>
            <button onClick={onClose} className="btn btn-secondary btn-sm">
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div style={{ padding: "1.5rem", overflowY: "auto", flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>
              Loading report details...
            </div>
          ) : reportData ? (
            <pre style={{
              background: "#060911",
              border: "1px solid #172138",
              borderRadius: "8px",
              padding: "1.25rem",
              fontSize: "0.85rem",
              lineHeight: "1.6",
              color: "#cbd5e1",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontFamily: "var(--font-mono)"
            }}>
              {reportData.content_markdown}
            </pre>
          ) : (
            <div style={{ color: "var(--crimson)" }}>Failed to load report.</div>
          )}
        </div>
      </div>
    </div>
  );
}
