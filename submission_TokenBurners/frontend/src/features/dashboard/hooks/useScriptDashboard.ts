import { useEffect, useMemo, useState } from "react";

import { fetchDashboard, fetchHealth, respondToScript, submitScript } from "../api/dashboardApi";
import type { ScriptFilter, ScriptRecord, SubmitScriptPayload } from "../types/dashboard";
import { latestClassifiedScript, latestEscalatedScript } from "../utils/format";

export function useScriptDashboard() {
  const [scripts, setScripts] = useState<ScriptRecord[]>([]);
  const [filter, setFilter] = useState<ScriptFilter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [healthMessage, setHealthMessage] = useState("agent running");

  async function refreshDashboard(preserveSelected = true) {
    try {
      const data = await fetchDashboard();
      setScripts(data.scripts);
      setError(null);

      if (!preserveSelected || !selectedId) {
        setSelectedId(data.scripts[0]?.script_id ?? null);
        return;
      }

      const stillExists = data.scripts.some((script) => script.script_id === selectedId);
      if (!stillExists) {
        setSelectedId(data.scripts[0]?.script_id ?? null);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshDashboard(false);

    fetchHealth()
      .then((data) => setHealthMessage(data.message))
      .catch(() => setHealthMessage("agent running"));

    const timer = window.setInterval(() => {
      void refreshDashboard(true);
    }, 5000);

    return () => window.clearInterval(timer);
  }, []);

  const filteredScripts = useMemo(() => {
    if (filter === "all") {
      return scripts;
    }
    return scripts.filter((script) => script.status === filter);
  }, [filter, scripts]);

  const selectedScript = useMemo(
    () => scripts.find((script) => script.script_id === selectedId) ?? null,
    [scripts, selectedId],
  );

  const uniqueClients = useMemo(() => new Set(scripts.map((script) => script.client_name)).size, [scripts]);
  const approvedCount = scripts.filter((script) => script.status === "approved").length;
  const waitingCount = scripts.filter((script) => script.status === "awaiting_response").length;
  const escalatedCount = scripts.filter(
    (script) => script.status === "escalated" || script.status === "call_requested",
  ).length;

  const lastClassified = latestClassifiedScript(scripts);
  const latestEscalation = latestEscalatedScript(scripts);

  async function handleSubmit(payload: SubmitScriptPayload) {
    try {
      setBusy(true);
      const created = await submitScript(payload);
      await refreshDashboard(false);
      setSelectedId(created.script_id);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to submit script");
    } finally {
      setBusy(false);
    }
  }

  async function handleRespond(responseText: string) {
    if (!selectedScript) {
      return;
    }

    try {
      setBusy(true);
      await respondToScript({ script_id: selectedScript.script_id, response: responseText });
      await refreshDashboard(true);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to send response");
    } finally {
      setBusy(false);
    }
  }

  return {
    approvedCount,
    busy,
    error,
    escalatedCount,
    filter,
    filteredScripts,
    handleRespond,
    handleSubmit,
    healthMessage,
    lastClassified,
    latestEscalation,
    loading,
    refreshDashboard,
    scripts,
    selectedId,
    selectedScript,
    setFilter,
    setSelectedId,
    uniqueClients,
    waitingCount,
  };
}
