import { useState } from "react";

import type { ScriptRecord } from "../types/dashboard";
import { formatTimestamp } from "../utils/format";

interface ScriptDetailProps {
  script: ScriptRecord | null;
  busy: boolean;
  onRespond: (responseText: string) => Promise<void>;
}

const cannedResponses = [
  "looks good 👍",
  "almost perfect but can you make the hook more punchy? also the CTA feels weak",
  "can we jump on a call?",
  "🔥",
  "this does not work at all",
];

export function ScriptDetail({ script, busy, onRespond }: ScriptDetailProps) {
  const [responseText, setResponseText] = useState("");

  async function submitResponse(text: string) {
    if (!text.trim()) {
      return;
    }

    await onRespond(text);
    setResponseText("");
  }

  if (!script) {
    return (
      <div className="col-aside">
        <div className="detail-header">
          <div className="detail-client">Select a script</div>
          <div className="detail-meta">Pick any row to inspect status, history, and actions.</div>
        </div>
      </div>
    );
  }

  const showRespond = script.status === "awaiting_response" || script.status === "pending_send";

  return (
    <div className="col-aside">
      <div className="detail-header">
        <div className="detail-client">{script.client_name}</div>
        <div className="detail-meta">
          {script.script_id} · {script.account_manager} · sent {formatTimestamp(script.sent_at)} · v{script.version}
        </div>
      </div>

      <div className="detail-section">
        <div className="detail-section-label">Script excerpt</div>
        <div className="script-box">{script.script_text}</div>
      </div>

      {script.revision_notes ? (
        <div className="detail-section">
          <div className="detail-section-label">Revision notes</div>
          <pre className="notes-box">{script.revision_notes}</pre>
        </div>
      ) : null}

      <div className="detail-section">
        <div className="detail-section-label">Event log</div>
        <div className="timeline">
          {script.history.map((entry) => (
            <div className="timeline-item" key={entry}>
              <span className="timeline-time">{entry.slice(1, 18)}</span>
              <span className="timeline-event">{entry.replace(/^\[[^\]]+\]\s*/, "")}</span>
            </div>
          ))}
        </div>
      </div>

      {showRespond ? (
        <div className="respond-section">
          <div className="detail-section-label">Simulate client response</div>
          <div className="response-grid">
            {cannedResponses.map((message) => (
              <button
                key={message}
                className={`action-btn${message.includes("does not work") ? " danger" : ""}`}
                disabled={busy}
                onClick={() => submitResponse(message)}
                type="button"
              >
                {message}
              </button>
            ))}
          </div>
          <div className="classify-input-wrap response-input-wrap">
            <input
              className="classify-input"
              placeholder="Type a custom client response"
              value={responseText}
              onChange={(event) => setResponseText(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  void submitResponse(responseText);
                }
              }}
            />
            <button
              className="classify-btn"
              disabled={busy}
              onClick={() => submitResponse(responseText)}
              type="button"
            >
              {busy ? "sending..." : "send →"}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
