import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./components/Dashboard";
import SimulationConsole from "./components/SimulationConsole";
import HistoryView from "./components/HistoryView";
import ScenarioCatalog from "./components/ScenarioCatalog";
import ReportModal from "./components/ReportModal";
import ScenarioSpecsModal from "./components/ScenarioSpecsModal";

import {
  getScenarios,
  getSimulationHistory,
  runSimulation,
  getSimulationDetail,
  checkTargetHealth
} from "./api";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [targetMode, setTargetMode] = useState("vulnerable"); // "vulnerable" or "remediated"
  const [targetUrl] = useState("http://localhost:8001");
  const [targetHealth, setTargetHealth] = useState(null);

  const [scenarios, setScenarios] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // Simulation execution state
  const [isSimulating, setIsSimulating] = useState(false);
  const [activeSimulation, setActiveSimulation] = useState(null);
  const [simError, setSimError] = useState(null);

  // Modals state
  const [viewingReportRunId, setViewingReportRunId] = useState(null);
  const [viewingSpecsScenarioId, setViewingSpecsScenarioId] = useState(null);

  // Initial data fetch
  const refreshData = async () => {
    try {
      const [scens, hist, health] = await Promise.all([
        getScenarios(),
        getSimulationHistory(),
        checkTargetHealth(targetUrl)
      ]);
      setScenarios(scens);
      setHistory(hist);
      setTargetHealth(health);
    } catch (err) {
      console.error("Failed to load initial data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(() => {
      checkTargetHealth(targetUrl).then(h => setTargetHealth(h));
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Launch a simulation
  const handleLaunchSimulation = async (scenarioId, overrideMode) => {
    const modeToUse = overrideMode || targetMode;
    setIsSimulating(true);
    setSimError(null);
    setActiveSimulation(null);
    setActiveTab("dashboard");

    try {
      const result = await runSimulation(scenarioId, targetUrl, modeToUse);
      setActiveSimulation(result);
      // Refresh history
      getSimulationHistory().then(h => setHistory(h));
    } catch (err) {
      setSimError(err.message || "Failed to execute simulation.");
    } finally {
      setIsSimulating(false);
    }
  };

  // Inspect run from history
  const handleInspectRun = async (runId) => {
    try {
      const detail = await getSimulationDetail(runId);
      setActiveSimulation(detail);
      setActiveTab("dashboard");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        targetHealth={targetHealth}
        targetMode={targetMode}
        setTargetMode={setTargetMode}
        onRefreshHealth={() => checkTargetHealth(targetUrl).then(h => setTargetHealth(h))}
      />

      {/* Main Content Area */}
      <main className="container" style={{ flex: 1, paddingTop: "1.75rem" }}>
        {/* Error Banner if any */}
        {simError && (
          <div className="glass-panel" style={{
            padding: "1rem 1.25rem",
            marginBottom: "1.5rem",
            borderLeft: "4px solid var(--crimson)",
            background: "rgba(239, 68, 68, 0.1)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <span style={{ fontSize: "1.25rem" }}>⚠️</span>
              <span style={{ color: "#f87171", fontSize: "0.9rem", fontWeight: 600 }}>
                {simError}
              </span>
            </div>
            <button onClick={() => setSimError(null)} className="btn btn-secondary btn-sm">✕</button>
          </div>
        )}

        {/* Target Offline Warning */}
        {targetHealth && !targetHealth.reachable && (
          <div className="glass-panel" style={{
            padding: "0.85rem 1.25rem",
            marginBottom: "1.5rem",
            borderLeft: "4px solid var(--amber)",
            background: "rgba(245, 158, 11, 0.08)",
            display: "flex",
            alignItems: "center",
            gap: "0.75rem"
          }}>
            <span style={{ fontSize: "1.2rem" }}>ℹ️</span>
            <div style={{ fontSize: "0.85rem", color: "#fbbf24" }}>
              <strong>Local Training Target Sandbox is currently offline on port 8001.</strong>
              <span style={{ marginLeft: "0.5rem", color: "var(--text-secondary)" }}>
                Ensure <code>py training_target/app/main.py</code> or docker is running to execute live HTTP simulations.
              </span>
            </div>
          </div>
        )}

        {/* Live Simulation Console (Visible when simulating or displaying results) */}
        {(isSimulating || activeSimulation) && (
          <SimulationConsole
            isRunning={isSimulating}
            simulationData={activeSimulation}
            onClose={() => setActiveSimulation(null)}
            onRerun={(scenId, mode) => handleLaunchSimulation(scenId, mode)}
            onViewReport={(runId) => setViewingReportRunId(runId)}
          />
        )}

        {/* Active Tab Views */}
        {loading ? (
          <div style={{ textAlign: "center", padding: "4rem", color: "var(--text-muted)" }}>
            Initializing sandbox environment...
          </div>
        ) : (
          <>
            {activeTab === "dashboard" && (
              <Dashboard
                scenarios={scenarios}
                history={history}
                targetMode={targetMode}
                targetHealth={targetHealth}
                onLaunchSimulation={(scenId) => handleLaunchSimulation(scenId)}
                onViewScenarioSpecs={(scenId) => setViewingSpecsScenarioId(scenId)}
              />
            )}

            {activeTab === "scenarios" && (
              <ScenarioCatalog
                scenarios={scenarios}
                onLaunchSimulation={(scenId) => handleLaunchSimulation(scenId)}
              />
            )}

            {activeTab === "history" && (
              <HistoryView
                history={history}
                onInspectRun={handleInspectRun}
                onViewReport={(runId) => setViewingReportRunId(runId)}
              />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid var(--border-subtle)",
        padding: "1.25rem 0",
        background: "var(--bg-primary)",
        color: "var(--text-muted)",
        fontSize: "0.8rem",
        textAlign: "center"
      }}>
        <div className="container">
          Black-Box Attack Simulator • Educational Sandbox • 🔒 Strict Loopback Confinement Enforced
        </div>
      </footer>

      {/* Modals */}
      {viewingReportRunId && (
        <ReportModal
          runId={viewingReportRunId}
          onClose={() => setViewingReportRunId(null)}
        />
      )}

      {viewingSpecsScenarioId && (
        <ScenarioSpecsModal
          scenarioId={viewingSpecsScenarioId}
          onClose={() => setViewingSpecsScenarioId(null)}
          onLaunch={(scenId) => handleLaunchSimulation(scenId)}
        />
      )}
    </div>
  );
}
