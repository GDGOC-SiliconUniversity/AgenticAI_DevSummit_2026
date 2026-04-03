# Submission Summary

## Team

**Team Name:** Nutranates
**Members:** 
Sandeep kumar Choudhury | Lead Developer
Anushka | n8n and integration
Aman Bhoi | UI/UX and frontend
**Contact Email:** sandeepchoudhury444@gmail.com

---

## Problem Statement

**Selected Problem:** Content Brief to Script Pipeline / Client Approval Bottleneck
**Problem Title:** Automated Script Approval Loop  

In content agencies, sending video scripts to clients for approval often stalls the production pipeline because clients delay, give vague replies, or request changes informally via disjointed email chains. This system resolves this operational failure by fully automating the email approval cadence, strictly classifying client feedback, structured task extraction, and automatically updating Airtable tracking—saving account managers hours of manual follow-ups and centralizing feedback.

---

## System Overview

The Script Approval Agent serves as a fully automated middleman between scriptwriters and clients. When a script is marked ready in Airtable, the system automatically writes to the client and ships a professional, version-tracked email. If the client fails to reply, the system automatically sends polite nudges at 24 and 48 hours, escalating to human managers at 72. When the client replies, an AI classification workflow automatically reads the response, decides if it's an approval, rejection, or revision, extracts structured action items for the writers, and updates the core tracking database.

---

## Tools and Technologies

| Tool or Technology | Version or Provider | What It Does in Your System |
|---|---|---|
| LangGraph | `langgraph>=0.2.0` | Orchestrates the state machine (workflow routing, managing steps, wait states, and conditional loops based on LLM outputs). |
| LangChain | `langchain>=0.3.0` | Wraps prompts and the LLM API to format variables safely and parse unstructured text into JSON/structured outputs. |
| Groq Llama 3 | `llama-3.1-8b-instant` | The brain of the agent; formats emails uniquely, classifies messy human text, and extracts structured feedback. |
| FastAPI | `fastapi>=0.115.0` | Provides the REST API backend so external webhooks/apps can start approvals and inject replies. |
| pyairtable | `pyairtable>=2.3.0` | The primary CRM/Database interface, used for maintaining script status, client contacts, and tracking state. |
| Vanilla JS / HTML | Frontend | Single-page Application (SPA) dashboard to visualize the Airtable data and manually dispatch/process agent workflows. |
| smtplib | Python Native | Handles the plain-text agent communication out to clients over Gmail. |

---

## LLM Usage

**Model(s) used:** Llama 3.1 8B Instant  
**Provider(s):** Groq  
**Access method:** API key (`GROQ_API_KEY`)  

| Step | LLM Input | LLM Output | Effect on System |
|---|---|---|---|
| 1. Format Email | `script_text`, `client_name`, `version`, `deadline_hours` | Professional plain-text email body | Used as the exact `$body` of the external SMTP email sent to the client. |
| 2. Classify Reply | The raw client reply (e.g. "Looks great but change the intro") | A JSON payload with `decision` (approved/revision/rejected) | Drives the LangGraph conditional edges, dictating which downstream nodes process the data. |
| 3. Extract Notes | Raw reply + the decision label | Plaintext markdown checklist of requested changes | Saved directly to Airtable so scriptwriters can execute the revisions immediately. |

---

## Algorithms and Logic

**State Machine (LangGraph):**
The core system is orchestrated via an explicit directed graph. The `ApprovalState` acts as a shared memory `TypedDict`. 
- **Wait loop**: When state reaches `wait_for_response`, a conditional edge checks `response_raw`. If empty, it routes to deterministic follow-up nodes based on the integer counter `follow_ups_sent` (which triggers emails and increments).
- **Classification Routing**: Once a response exists, the LLM processes it via a few-shot prompt to guarantee JSON output. A conditional edge routes the flow based specifically on the `status` string extracted.
- **Resilience**: The classifier node explicitly handles JSON parse failures by safely coercing malformed LLM outputs into a default `revision` state to prevent pipeline crashes.

---

## Deterministic vs Agentic Breakdown

**Estimated breakdown:**

| Layer | Percentage | Description |
|---|---|---|
| Deterministic automation | 75% | State routing, wait loops, Airtable CRUD operations, SMTP transport, follow-up counting, and the FastAPI API surface. |
| LLM-driven and agentic | 25% | Email content generation, intent classification of messy human replies, and parsing messy requirements into developer-ready task lists. |

The agentic layer allows the system to handle the sheer unpredictability of human responses ("yeah I guess that works lol"). If replaced by a fixed script, we would have to enforce rigid, annoying form submissions from clients (like "Click a button to approve"). By utilizing an LLM, the client gets the premium, frictionless experience of simply replying to an email, while the agency gets the benefits of structured data entries.

---

## Edge Cases Handled

| Edge Case | How Your System Handles It |
|---|---|
| Ambiguous / messy replies | Few-shot prompting trains the classifier on edge cases like "looks fine, just cut the end", returning `revision`. |
| Unresponsive clients | The Graph explicitly maintains a `follow_ups_sent` integer; tracking 24/48h cadences and routing to an `escalate` node at 72 hours. |
| Requesting a phone call | Classifier specifically looks for "call_requested" intent; routes to a distinct `handle_call_request` node that pauses the workflow. |
| LLM Hallucinations / Syntax | Classifier output is stripped of markdown code blocks. If `json.loads` fails, a catastrophic safety fallback forces a `revision` decision. |

---

## Repository

**GitHub Repository Link:** https://github.com/SANDEEP2630A/content-approval-loop_Nutranates  
**Branch submitted:** main  
**Commit timestamp of final submission:** `f347ca59639dd3ec2e5acc2a88c6be30bf0d7f81` (around 2026-04-03 11:20:18 UTC)  

---

## Deployment

**Is your system deployed?** No  

---

## Known Limitations

- **Email Interception**: Currently, `/receive-reply` is triggered manually via the dashboard or a webhook. A direct IMAP poller reading the Gmail inbox continuously was left out due to time constraints, so client replies must be fed to the endpoint.
- **Client Channel**: The state implies `client_channel` but the workflow currently only supports email notifications via SMTP.
- **In-Memory State**: The Langgraph state cache (`_state_store` in `main.py`) operates in memory. If the Uvicorn server restarts, active wait-states for pending approvals are lost unless resuscitated explicitly from the Airtable records.

---

## Anything Else

The frontend dashboard serves as a completely standalone HTML artifact served right from the FastAPI instance over cross-origin paths, meaning the solution requires zero external web server configurations to test immediately. We recently migrated the core intelligence engine from Gemini to Groq (Llama 3.1 8B) for significant latency improvements in classification nodes!
