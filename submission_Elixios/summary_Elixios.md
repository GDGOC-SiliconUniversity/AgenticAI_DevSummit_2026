# Submission Summary

## Team

**Team Name:** Elixios
**Members:**
Shriyansh Dash | Lead Developer & Agent Architect
Durga Prasad Sarangi | Backend Developer & Integration Engineer

**Contact Email:** shriyanshdash12@gmail.com

---

## Problem Statement

**Selected Problem:** PS-01
**Problem Title:** Client Onboarding

When a new client is signed at Scrollhouse, the onboarding process requires manually creating a Google Drive folder structure, setting up a Notion client hub, adding a CRM record in Airtable, and sending welcome and confirmation emails — all done by hand, across four different tools, by the account manager. This takes 45–90 minutes per client and is error-prone. Our system eliminates this entirely by automating the full onboarding sequence end-to-end the moment a form is submitted, reducing it to under 3 minutes with zero manual intervention.

---

## System Overview

When a new client form is submitted through the web UI, the system triggers a multi-step LangGraph agent pipeline. The agent first validates the input and checks for duplicate clients in Airtable. If the client is new and valid, it generates a personalised welcome email using Gemini and sends it to the billing contact. It then creates a structured Google Drive folder with five subfolders, sets access permissions for the account manager and billing contact, duplicates a Notion template page and populates it with client details and a content calendar, and writes a complete CRM record to Airtable. Finally, it generates an internal completion summary email for the account manager and logs the full run. Every step is traced via LangSmith. The frontend shows a live workflow timeline as the agent runs.

---

## Tools and Technologies

| Tool or Technology | Version or Provider | What It Does in Your System |
|---|---|---|
| LangGraph | 0.2.28 | Orchestrates the 9-node agent state machine with conditional halt edges |
| LangChain | 0.3.3 | Provides the LLM interface and message formatting for Gemini calls |
| Google Gemini | gemini-2.5-flash via Google AI API | Generates welcome emails and completion summary emails |
| FastAPI | 0.115.0 | Exposes the POST /webhook/onboard endpoint that triggers the agent |
| Uvicorn | 0.30.6 | ASGI server that runs the FastAPI app |
| pyairtable | 2.3.3 | Creates and queries records in the Airtable Clients CRM table |
| notion-client | 2.2.1 | Creates client hub pages under a parent Notion page with content calendar |
| google-api-python-client | 2.149.0 | Creates Google Drive folder structures and sets sharing permissions |
| google-auth | 2.35.0 | Authenticates the Drive service account |
| LangSmith | 0.1.131 | Traces every node execution for full observability |
| Gmail SMTP | Python smtplib / Gmail App Password | Sends welcome and completion emails via SSL on port 465 |
| Next.js | 16.2.2 | Frontend UI with form, live workflow timeline, and results display |
| React | 19.2.4 | Component layer for AgentForm, WorkflowTimeline, AgentResults |
| python-dotenv | 1.0.1 | Loads environment variables from .env at runtime |
| Pydantic | 2.9.2 | Validates and parses the incoming webhook payload |

---

## LLM Usage

**Model(s) used:** gemini-2.5-flash
**Provider(s):** Google AI (via langchain-google-genai)
**Access method:** API key

| Step | LLM Input | LLM Output | Effect on System |
|---|---|---|---|
| send_welcome_email | System prompt defining Scrollhouse brand voice + user prompt with brand name, account manager name, contract start date, deliverable count, and kickoff calendar link | A personalised welcome email body (max 180 words) with structured sections: team intro, first two weeks expectations, kickoff CTA | The generated HTML is sent via Gmail SMTP to the billing contact email. If the LLM produces a poor output the email still sends — quality is LLM-dependent |
| send_completion_summary | System prompt for internal ops tone + user prompt with account manager name, brand name, Drive link, Notion link, Airtable link, and any errors from the run | A concise internal ops summary email (max 120 words) confirming all systems are set up and flagging any issues | Sent to the account manager's email. Gives the AM a single-message confirmation with all resource links |

---

## Algorithms and Logic

**Graph structure:** The agent uses a LangGraph `StateGraph` with a `ReducerState` that merges list fields (`errors`, `flags`, `completed_steps`) via `operator.add` so each node appends without overwriting prior state.

**Conditional halt edges:** After `validate_input` and `duplicate_check`, a `_should_halt` function checks the `halt` boolean in state. If true, the graph skips directly to `log_onboarding` and terminates. All other edges are linear.

**Retry logic:** `create_drive_folder`, `create_notion_hub`, and `add_airtable_record` each attempt the operation twice with a 3-second sleep between attempts before falling back to an alert email.

**Partial record prevention:** Before writing to Airtable, both the node (`add_airtable_record`) and the client (`create_client_record`) independently check that all required fields are non-null. If any are missing, the write is skipped and the AM is alerted.

**Duplicate detection:** `find_client_by_brand` uses pyairtable's `match()` formula to query Airtable for an existing record with the same `brand_name` before proceeding.

**Content calendar generation:** `_generate_content_calendar` distributes `deliverable_count` slots evenly across 30 days using `ceil(interval * (i+1))` offsets from the contract start date.

**Permission model:** Billing contact gets `commenter` access on Drive. Account manager gets `writer` access. Both are set via the Drive API after folder creation.

---

## Deterministic vs Agentic Breakdown

| Layer | Percentage | Description |
|---|---|---|
| Deterministic automation | 75% | Input validation, duplicate check via Airtable query, Drive folder creation and permission setting, Notion page creation with structured content, Airtable record write, email dispatch, retry logic, halt conditions, logging |
| LLM-driven and agentic | 25% | Welcome email body generation (tone, structure, personalisation) and completion summary generation (contextual ops update with error awareness) |

**Total: 100%**

The agentic layer handles all human-facing communication. If the LLM were replaced with a fixed template, the emails would be generic and robotic — the welcome email would lose personalisation to the brand and account manager, and the completion summary would not contextually reference errors or missing steps. The LLM reads the full run context (including errors) and adjusts its output accordingly, which a fixed script cannot do.

---

## Edge Cases Handled

| Edge Case | How Your System Handles It |
|---|---|
| Past contract start date | `validate_input` compares date against UTC today. If in the past, sets `halt=True`, appends `past_contract_date` flag, sends alert email to AM, and stops pipeline |
| Unknown account manager | `validate_input` checks name against `TEAM_ROSTER` dict. If not found, halts pipeline and sends alert to `ops@scrollhouse.com` |
| Duplicate client in Airtable | `duplicate_check` queries Airtable before any work begins. If a record exists, halts and alerts AM with the existing record ID |
| Welcome email bounce | `send_welcome_email` catches `EmailBounceError` separately, flags the AM via alert email, and continues the pipeline rather than halting |
| Drive API failure | Retries once after 3 seconds. If both attempts fail, alerts AM and continues with remaining steps |
| Notion API failure | Same retry-once pattern as Drive. Pipeline continues even if Notion fails |
| Airtable partial record | Both node and client-level checks verify all 9 required fields are present before attempting write. Skips write and alerts AM with the list of missing fields if any are null |

**Not implemented:** Email delivery confirmation (no webhook from Gmail SMTP), Drive subfolder permission inheritance verification, Notion template content duplication (creates a fresh page rather than a true template clone).

---

## Repository

**GitHub Repository Link:** https://github.com/shrixtacy/ScrollHouse-AgenticAI
**Branch submitted:** feature/gmail-smtp-migration
**Commit timestamp of final submission:** fc887af1d8fafabfbd8014ad860c74df2c8536ab — 2026-04-03 11:18:41 UTC

---

## Deployment

**Is your system deployed?** Yes

**Deployment link:** (add Railway backend URL here once deployed)
**Platform used:** Railway (backend) + Vercel (frontend)
**What can be tested at the link:** Full client onboarding form — submit a new client and watch the 9-step agent pipeline run live, with Drive folder, Notion hub, Airtable record, and emails created in real time.

---

## Known Limitations

- Gmail SMTP has a daily send limit (~500 emails/day). Not suitable for high-volume production without switching to SendGrid or AWS SES.
- Notion page creation does not clone the template's block content — it creates a fresh structured page. True template duplication requires Notion's duplicate API which is not publicly available.
- The frontend timeline is partially simulated during loading (steps animate at 1.8s intervals) and then replaced with actual completed steps from the API response. It does not stream real-time node progress.
- Google Drive `webViewLink` is only accessible to users the folder has been shared with. The link in the UI will show a permissions error for anyone not explicitly granted access.
- LangSmith tracing requires a valid `LANGSMITH_API_KEY`. If the key is missing or invalid, tracing silently fails but the pipeline continues.
- The system does not support concurrent onboarding runs — LangGraph graph is compiled once at startup and invoked synchronously per request.

---

## Anything Else

The system is fully functional end-to-end with real API integrations — no mocked services. Every step in the pipeline creates actual resources: a real Google Drive folder with subfolders and permissions, a real Notion page with content calendar, a real Airtable CRM record, and real emails sent via Gmail. LangSmith tracing is active and every node execution is observable at smith.langchain.com under the `scrollhouse-ps01` project.
