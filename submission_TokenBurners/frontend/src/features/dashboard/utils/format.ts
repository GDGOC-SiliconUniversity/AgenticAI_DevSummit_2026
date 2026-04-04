import type { ScriptRecord, ScriptStatus } from "../types/dashboard";

export function formatTimestamp(value: string): string {
  if (!value) {
    return "n/a";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function scriptPreview(text: string): string {
  if (text.length <= 96) {
    return text;
  }
  return `${text.slice(0, 93)}...`;
}

export function statusLabel(status: ScriptStatus): string {
  const labels: Record<ScriptStatus, string> = {
    awaiting_response: "waiting",
    approved: "approved",
    needs_revision: "revisions",
    rejected: "rejected",
    call_requested: "call requested",
    escalated: "escalated",
    pending_send: "queued",
  };

  return labels[status];
}

export function statusClassName(status: ScriptStatus): string {
  const classes: Record<ScriptStatus, string> = {
    awaiting_response: "s-waiting",
    approved: "s-approved",
    needs_revision: "s-revision",
    rejected: "s-escalated",
    call_requested: "s-sent",
    escalated: "s-escalated",
    pending_send: "s-sent",
  };

  return classes[status];
}

export function latestClassifiedScript(scripts: ScriptRecord[]): ScriptRecord | undefined {
  return [...scripts]
    .filter((script) => Boolean(script.classification))
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))[0];
}

export function latestEscalatedScript(scripts: ScriptRecord[]): ScriptRecord | undefined {
  return [...scripts]
    .filter((script) => script.status === "escalated" || script.status === "call_requested")
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))[0];
}
