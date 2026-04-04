import { Masthead } from "../features/dashboard/components/Masthead";
import { MetricsRow } from "../features/dashboard/components/MetricsRow";
import { ScriptDetail } from "../features/dashboard/components/ScriptDetail";
import { ScriptQueue } from "../features/dashboard/components/ScriptQueue";
import { SubmitPanel } from "../features/dashboard/components/SubmitPanel";
import { TickerBar } from "../features/dashboard/components/TickerBar";
import { useScriptDashboard } from "../features/dashboard/hooks/useScriptDashboard";

function App() {
  const {
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
    selectedId,
    selectedScript,
    setFilter,
    setSelectedId,
    scripts,
    uniqueClients,
    waitingCount,
  } = useScriptDashboard();

  return (
    <div className="shell">
      <Masthead healthMessage={healthMessage} clientCount={uniqueClients} />
      <TickerBar
        escalated={
          latestEscalation
            ? `${latestEscalation.script_id} · ${latestEscalation.status.replace("_", " ")}`
            : "no escalation yet"
        }
        lastClassified={
          lastClassified
            ? `"${lastClassified.client_response}" → ${lastClassified.classification}`
            : "waiting for first client reply"
        }
        queue={`${waitingCount} awaiting response · ${scripts.length} total tracked`}
      />
      <MetricsRow total={scripts.length} approved={approvedCount} waiting={waitingCount} escalated={escalatedCount} />

      {error ? <div className="error-banner">{error}</div> : null}
      {loading ? <div className="loading-banner">Loading dashboard...</div> : null}

      <div className="top-actions">
        <button className="action-btn refresh-btn" onClick={() => void refreshDashboard(true)} type="button">
          refresh dashboard
        </button>
      </div>

      <div className="two-col">
        <ScriptQueue
          filter={filter}
          onFilterChange={setFilter}
          onSelect={setSelectedId}
          scripts={filteredScripts}
          selectedId={selectedId}
        />
        <div className="aside-stack">
          <SubmitPanel busy={busy} onSubmit={handleSubmit} />
          <ScriptDetail busy={busy} onRespond={handleRespond} script={selectedScript} />
        </div>
      </div>

      <div className="bottom-bar">
        <span>ScriptAgent React demo — backend-connected operator view</span>
        <span>Frontend polls every 5s · Vite + React + TypeScript</span>
      </div>
    </div>
  );
}

export default App;
