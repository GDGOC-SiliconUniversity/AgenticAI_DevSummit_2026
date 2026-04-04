import type { ScriptRecord, SubmitScriptPayload, SubmitResponsePayload } from "../types/dashboard";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  return fetch(`${apiBaseUrl}${path}`, init);
}

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function fetchHealth(): Promise<{ message: string }> {
  return readJson<{ message: string }>(await apiFetch("/"));
}

export async function fetchDashboard(): Promise<{ scripts: ScriptRecord[] }> {
  return readJson<{ scripts: ScriptRecord[] }>(await apiFetch("/dashboard"));
}

export async function fetchScriptStatus(scriptId: string): Promise<ScriptRecord> {
  return readJson<ScriptRecord>(await apiFetch(`/status/${scriptId}`));
}

export async function submitScript(payload: SubmitScriptPayload): Promise<ScriptRecord> {
  return readJson<ScriptRecord>(
    await apiFetch("/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function respondToScript(payload: SubmitResponsePayload): Promise<ScriptRecord> {
  return readJson<ScriptRecord>(
    await apiFetch("/respond", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}
