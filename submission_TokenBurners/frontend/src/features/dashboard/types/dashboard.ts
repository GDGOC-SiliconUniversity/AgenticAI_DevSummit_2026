export type ScriptStatus =
  | "awaiting_response"
  | "approved"
  | "needs_revision"
  | "rejected"
  | "call_requested"
  | "escalated"
  | "pending_send";

export interface ScriptRecord {
  script_id: string;
  script_text: string;
  client_name: string;
  client_contact: string;
  account_manager: string;
  preferred_channel: "email" | "whatsapp";
  sla_hours: number;
  status: ScriptStatus;
  follow_up_count: number;
  client_response: string;
  classification: string;
  revision_notes: string;
  history: string[];
  sent_at: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface SubmitScriptPayload {
  script_id: string;
  script_text: string;
  client_name: string;
  client_contact: string;
  account_manager: string;
  preferred_channel: "email" | "whatsapp";
  sla_hours: number;
}

export interface SubmitResponsePayload {
  script_id: string;
  response: string;
}

export type ScriptFilter = "all" | "awaiting_response" | "approved" | "needs_revision" | "escalated" | "call_requested";
