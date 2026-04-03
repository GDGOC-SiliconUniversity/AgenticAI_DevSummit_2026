import type { ScriptFilter, ScriptRecord } from "../types/dashboard";
import { formatTimestamp, scriptPreview, statusClassName, statusLabel } from "../utils/format";

interface ScriptQueueProps {
  filter: ScriptFilter;
  scripts: ScriptRecord[];
  selectedId: string | null;
  onFilterChange: (filter: ScriptFilter) => void;
  onSelect: (scriptId: string) => void;
}

const filters: { label: string; value: ScriptFilter }[] = [
  { label: "All", value: "all" },
  { label: "Waiting", value: "awaiting_response" },
  { label: "Approved", value: "approved" },
  { label: "Revisions", value: "needs_revision" },
  { label: "Escalated", value: "escalated" },
  { label: "Calls", value: "call_requested" },
];

export function ScriptQueue({
  filter,
  scripts,
  selectedId,
  onFilterChange,
  onSelect,
}: ScriptQueueProps) {
  return (
    <div className="col-main">
      <div className="section-header">
        <span>Script queue</span>
        <span>{scripts.length} scripts</span>
      </div>
      <div className="filter-row">
        {filters.map((item) => (
          <button
            key={item.value}
            className={`filter-btn${filter === item.value ? " active" : ""}`}
            onClick={() => onFilterChange(item.value)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </div>
      <div className="script-list">
        {scripts.map((script) => (
          <button
            key={script.script_id}
            className={`script-row${selectedId === script.script_id ? " selected" : ""}`}
            onClick={() => onSelect(script.script_id)}
            type="button"
          >
            <div className="script-id">
              {script.script_id}
              {script.version > 1 ? ` v${script.version}` : ""}
            </div>
            <div>
              <div className="script-client">{script.client_name}</div>
              <div className="script-preview">{scriptPreview(script.script_text)}</div>
            </div>
            <div>
              <span className={`status-pill ${statusClassName(script.status)}`}>{statusLabel(script.status)}</span>
            </div>
            <div className="followup-count">
              {script.follow_up_count > 0
                ? `${script.follow_up_count} follow-up${script.follow_up_count > 1 ? "s" : ""}`
                : formatTimestamp(script.sent_at)}
            </div>
          </button>
        ))}
        {scripts.length === 0 ? <div className="empty-state">No scripts match this filter.</div> : null}
      </div>
    </div>
  );
}
