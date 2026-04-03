import { type FormEvent, useState } from "react";

import type { SubmitScriptPayload } from "../types/dashboard";

interface SubmitPanelProps {
  onSubmit: (payload: SubmitScriptPayload) => Promise<void>;
  busy: boolean;
}

const initialForm: SubmitScriptPayload = {
  script_id: "",
  script_text: "",
  client_name: "",
  client_contact: "",
  account_manager: "",
  preferred_channel: "email",
  sla_hours: 48,
};

export function SubmitPanel({ onSubmit, busy }: SubmitPanelProps) {
  const [form, setForm] = useState<SubmitScriptPayload>(initialForm);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(form);
    setForm(initialForm);
  }

  return (
    <div className="detail-section">
      <div className="detail-section-label">Submit a new script</div>
      <form className="submit-form" onSubmit={handleSubmit}>
        <input
          className="field"
          placeholder="Script ID"
          value={form.script_id}
          onChange={(event) => setForm({ ...form, script_id: event.target.value })}
          required
        />
        <input
          className="field"
          placeholder="Client name"
          value={form.client_name}
          onChange={(event) => setForm({ ...form, client_name: event.target.value })}
          required
        />
        <input
          className="field"
          placeholder="Client contact"
          value={form.client_contact}
          onChange={(event) => setForm({ ...form, client_contact: event.target.value })}
          required
        />
        <input
          className="field"
          placeholder="Account manager"
          value={form.account_manager}
          onChange={(event) => setForm({ ...form, account_manager: event.target.value })}
          required
        />
        <div className="inline-fields">
          <select
            className="field"
            value={form.preferred_channel}
            onChange={(event) =>
              setForm({
                ...form,
                preferred_channel: event.target.value as SubmitScriptPayload["preferred_channel"],
              })
            }
          >
            <option value="email">email</option>
            <option value="whatsapp">whatsapp</option>
          </select>
          <input
            className="field"
            min={1}
            placeholder="SLA"
            type="number"
            value={form.sla_hours}
            onChange={(event) => setForm({ ...form, sla_hours: Number(event.target.value) || 48 })}
          />
        </div>
        <textarea
          className="field field-area"
          placeholder="Paste the script text here"
          value={form.script_text}
          onChange={(event) => setForm({ ...form, script_text: event.target.value })}
          required
        />
        <button className="classify-btn submit-btn" disabled={busy} type="submit">
          {busy ? "submitting..." : "submit script →"}
        </button>
        <p className="form-note">
          The agent generates the rest automatically after submission: status, timestamps, history, follow-up count,
          classification, and revision notes.
        </p>
      </form>
    </div>
  );
}
