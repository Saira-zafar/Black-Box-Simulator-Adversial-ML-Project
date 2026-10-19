/**
 * API Service for interacting with Black-Box Attack Simulator backend.
 */

const BASE_URL = "http://localhost:8000/api";

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return await res.json();
  } catch (err) {
    return { status: "offline", error: err.message };
  }
}

export async function checkTargetHealth(targetUrl = "http://localhost:8001") {
  try {
    const res = await fetch(`${BASE_URL}/target/health?url=${encodeURIComponent(targetUrl)}`);
    return await res.json();
  } catch (err) {
    return { reachable: false, error: err.message };
  }
}

export async function getScenarios() {
  const res = await fetch(`${BASE_URL}/scenarios`);
  if (!res.ok) throw new Error("Failed to fetch scenarios");
  return await res.json();
}

export async function getScenarioDetail(scenarioId) {
  const res = await fetch(`${BASE_URL}/scenarios/${scenarioId}`);
  if (!res.ok) throw new Error("Failed to fetch scenario details");
  return await res.json();
}

export async function runSimulation(scenarioId, targetUrl, targetMode) {
  const res = await fetch(`${BASE_URL}/simulations/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: scenarioId,
      target_url: targetUrl,
      target_mode: targetMode
    })
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Simulation execution failed");
  }
  return await res.json();
}

export async function getSimulationHistory() {
  const res = await fetch(`${BASE_URL}/simulations/history`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return await res.json();
}

export async function getSimulationDetail(runId) {
  const res = await fetch(`${BASE_URL}/simulations/${runId}`);
  if (!res.ok) throw new Error("Failed to fetch simulation details");
  return await res.json();
}

export async function getReport(runId) {
  const res = await fetch(`${BASE_URL}/reports/${runId}`);
  if (!res.ok) throw new Error("Failed to fetch report");
  return await res.json();
}

export function getReportDownloadUrl(runId) {
  return `${BASE_URL}/reports/${runId}/markdown`;
}
