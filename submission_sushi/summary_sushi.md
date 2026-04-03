# Submission Summary

## Team

**Team Name:** sushi  
**Members:** Ayushi Singh | Solo Developer  
**Contact Email:** ayusingh7005@gmail.com  

---

## Problem Statement

**Selected Problem:** PS-03  
**Problem Title:** Content Approval Loop  

Scrollhouse manages 22 active clients with 8 to 15 scripts awaiting approval at any point in time. The current process is entirely manual — scripts are sent via WhatsApp or email with no centralised tracking, follow-ups are done from memory, and client responses are frequently missed or lost. The business cost is direct: a client approved a script on WhatsApp that was never seen, causing an 11-day delay that missed a product launch window. Two clients independently reduced their monthly spend citing approval delays as the reason.

---

## System Overview

When a scriptwriter marks a script as ready for approval, the agent triggers automatically. It fetches the script content and client details from the database, retrieves past interaction history using semantic search to personalise the message tone, and sends a tailored approval request to the client via WhatsApp or email. If the client does not respond, the agent sends a polite follow-up at 24 hours and an urgent follow-up at 48 hours — both written by an LLM with awareness of the previous messages. At 72 hours with no response, the agent generates a detailed escalation brief and sends it to the account manager. When the client does reply — whether formally or informally — Claude Sonnet reads the message, classifies the intent, and resolves the outcome: approved scripts move to the production queue, revision requests are extracted into structured notes and the scriptwriter is notified, and rejections are escalated to the account manager.

---

## Tools and Technologies

| Tool or Technology | Version or Provider | What It Does in Your System |
|---|---|---|
| LangGraph | @langchain/langgraph v1.2.0 | Orchestrates the 8-node stateful agent graph, manages interrupt/resume between phases, persists state via Supabase checkpointer |
| LangChain | @langchain/core v1.2.30 | LLM abstraction layer, prompt construction, tool binding |
| Claude Haiku | claude-haiku-4-5-20251001 / Anthropic | Writes personalised approval request messages and follow-up messages |
| Claude Sonnet | claude-sonnet-4-6 / Anthropic | Classifies client replies, extracts structured revision notes, generates escalation briefs for account managers |
| OpenAI Embeddings | text-embedding-3-small / OpenAI | Generates 1536-dimension vector embeddings of client interaction history for semantic retrieval |
| Supabase PostgreSQL | Supabase | Stores scripts, clients, approval threads, audit log, and LangGraph checkpoint state |
| Supabase pgvector | Supabase | Vector store for client memory — enables semantic search over past interactions |
| Twilio WhatsApp | Twilio API | Sends outbound approval messages and follow-ups via WhatsApp, receives inbound client replies via webhook |
| Resend | Resend API | Sends approval requests, follow-ups, and escalation notifications via email |
| Vercel Cron | Vercel | Runs the approval monitor daily — checks all active threads and resumes the agent with the appropriate follow-up action |
| Next.js API Routes | Next.js 16 | Handles the scriptwriter trigger endpoint, Twilio inbound webhook, and cron monitor endpoint |
| LangSmith | LangSmith API | Traces every node execution, LLM call, routing decision, and output for full observability |
| Vercel | Vercel | Production deployment platform |

---

## LLM Usage

**Model(s) used:** claude-haiku-4-5-20251001, claude-sonnet-4-6  
**Provider(s):** Anthropic  
**Access method:** API key via @langchain/anthropic  

| Step | LLM Input | LLM Output | Effect on System |
|---|---|---|---|
| generateApprovalRequest | Script title, client name, past client memory context (top 3 RAG results), review link | Personalised approval request message body (under 120 words) | Message is sent to client via Twilio or Resend |
| generateFollowUp (24h) | Script title, client name, follow-up count, tone instruction (polite) | Follow-up message body referencing original request | Sent to client via preferred channel, thread status updated to follow_up_1_sent |
| generateFollowUp (48h) | Script title, client name, follow-up count, tone instruction (urgent) | Urgent follow-up message body stating production is blocked | Sent to client via preferred channel, thread status updated to follow_up_2_sent |
| classifyResponse | Script title, client name, raw client reply text | JSON object with classification (approved / revision_requested / rejected / call_requested / partial_approval / ambiguous), approved sections, revision notes, rejection reason, confidence level | Routes the graph to the correct resolution path |
| generateEscalation | Script title, client name, contact details, timestamps of all contact attempts, channel used | Escalation brief (under 150 words) summarising the situation and recommending a next action | Sent to account manager via email, script status updated to escalated |

---

## Algorithms and Logic

**RAG — Client Memory Retrieval**  
Before writing any message, the agent queries the client_memories table in Supabase using pgvector. The query is a natural language string describing the context — the client name, script title, and communication purpose. This is embedded using OpenAI text-embedding-3-small (1536 dimensions) and matched against stored memory vectors using cosine similarity via the match_client_memories RPC function. The top 5 results are retrieved and injected into the message generation prompt to personalise tone and approach.

**LangGraph Node Structure and Transition Conditions**  
The graph has 8 nodes: fetchContext, fetchClientMemory, generateApprovalRequest, sendApprovalMessage, waitForResponse, generateFollowUp, classifyResponse, generateEscalation, resolveApproval. After sendApprovalMessage, the graph reaches waitForResponse which calls interrupt() and pauses completely, saving full state to Supabase via the checkpointer. The graph resumes when the cron or webhook calls resumeApprovalFlow() with a Command containing the resume action. Routing after waitForResponse is conditional: response → classifyResponse, follow_up_1 or follow_up_2 → generateFollowUp, escalate → generateEscalation. After generateFollowUp, if followUpCount is less than 2 the graph returns to waitForResponse; if 2 or more it routes to generateEscalation.

**Response Classification Logic**  
Claude Sonnet is prompted with a strict JSON schema and a temperature of 0.1 to minimise variation. The classification handles informal approvals (thumbs up, "looks good", "yeah go ahead"), partial approvals (approves some sections, requests changes to others), call requests, and ambiguous responses. A fallback handles JSON parse failures by defaulting to ambiguous classification and flagging for manual review.

**Follow-up Timing Logic**  
The cron monitor calculates elapsed hours since the last send timestamp for each active thread. If status is request_sent and elapsed time exceeds 24 hours, action is follow_up_1. If status is follow_up_1_sent and elapsed time exceeds 24 hours, action is follow_up_2. If status is follow_up_2_sent and elapsed time exceeds 24 hours, action is escalate. This logic runs in the approval-monitor cron route.

**Retry and Fallback Behaviour**  
If RAG retrieval fails, the agent proceeds with an empty memory context rather than failing. If the classification JSON cannot be parsed, the system defaults to ambiguous and notifies the account manager for manual review. If message delivery fails, the error is logged to the audit_log table and returned as a partial state error without crashing the graph.

---

## Deterministic vs Agentic Breakdown

**Estimated breakdown:**

| Layer | Percentage | Description |
|---|---|---|
| Deterministic automation | 65% | Trigger detection, time elapsed calculation, routing decisions, all Supabase reads and writes, Twilio and Resend API calls, status updates, audit logging, webhook matching, cron scheduling |
| LLM-driven and agentic | 35% | Approval message generation, follow-up message generation, client response classification, revision note extraction, escalation brief generation, RAG-based memory personalisation |

**Total: 100%**

If the LLM were replaced with a fixed script, the system would lose the ability to handle natural human language. A fixed conditional cannot classify "looks good 👍" as an approval, extract "change the CTA but keep the hook" as a structured revision note, personalise message tone to match a specific client's communication style, or synthesise 72 hours of conversation history into a coherent escalation brief. The deterministic layer handles reliability; the agentic layer handles judgment.

---

## Edge Cases Handled

| Edge Case | How Your System Handles It |
|---|---|
| Client approves with informal language ("looks good", "👍", "yeah go ahead") | Claude Sonnet classifies with low temperature (0.1) and is explicitly prompted to recognise informal approval signals. Returns classification: approved with high confidence. |
| Client requests changes to some sections but approves others (partial approval) | Claude Sonnet classifies as partial_approval, extracts approved_sections and revision_notes as separate fields. Both are stored and the scriptwriter is notified with the full breakdown. |
| Client requests a call instead of written feedback | Classified as call_requested. Automated follow-up loop is paused (is_paused set to true). Account manager is notified immediately with instructions to schedule the call. |
| RAG retrieval fails (OpenAI API error) | Caught in a try/catch block. Agent proceeds with empty client memory context. Non-fatal — message is still generated and sent, just without personalisation context. |
| No active approval thread found for incoming Twilio webhook | Webhook always returns 200 to Twilio to prevent retries. Warning is logged. No graph is resumed. |
| Script already approved or closed when trigger fires | Trigger route checks script status before starting the graph. Returns 400 with a clear error message. Graph is not started. |
| Active approval thread already exists for the same script | Trigger route checks for existing non-terminal threads. Returns 409 Conflict if one exists. Prevents duplicate loops. |
| Classification JSON cannot be parsed | Falls back to ambiguous classification. Account manager is notified for manual review. System does not crash. |

**Edge cases from the problem statement not implemented:**  
Version mismatch detection (client comparing against wrong script version) — the system includes version labels in every message but does not actively detect if the client references an older version. Manual account manager review handles this case.

---

## Repository

**GitHub Repository Link:** https://github.com/ayu2912/script_approval_agent  
**Branch submitted:** main  
**Commit timestamp of final submission:** (paste your latest commit hash here after final push)

The repository is public. The README contains environment setup instructions, required API keys, and a sample flow to test with.

---

## Deployment

**Is your system deployed?** Yes  

**Deployment link:** https://script-approval-agent.vercel.app  
**Platform used:** Vercel  
**What can be tested at the link:** Dashboard for viewing scripts and clients, HITL review queue, approval trigger endpoint at /api/approval/trigger/[scriptId], Twilio webhook at /api/webhooks/twilio, approval monitor cron at /api/cron/approval-monitor  

---

## Known Limitations

- The approval monitor cron runs once daily at 9am due to Vercel Hobby plan restrictions. In production this would run hourly. Follow-up timing is therefore approximate rather than exact.
- Inbound email replies are not automatically classified. Only WhatsApp replies are handled via Twilio webhook. Email responses currently require manual input via the dashboard.
- Notion and Airtable integration is not implemented — API keys were unavailable during the build window. Revision tasks are communicated via email notification to the account manager.
- Twilio sandbox constraints mean all clients share one sender number and must opt in to receive WhatsApp messages. This is a sandbox limitation and not an architectural one.
- Call scheduling is not automated. When a client requests a call, the agent pauses the follow-up loop and notifies the account manager, but cannot book the call itself.
- Version mismatch detection is partial — version labels are included in every message but the agent does not actively detect if a client is referencing an outdated script version.

---

## Anything Else

The system is built as a direct extension of Greenlit, an existing production content agency SaaS. All core infrastructure — Supabase client, LangGraph checkpointer, Twilio and Resend integrations, authentication, and the existing agent graph — was inherited from the base project. The PS-03 approval agent adds 13 new files on top of this foundation: 1 database migration, 2 type and graph files, 8 LangGraph nodes, and 3 API routes. LangSmith tracing is active on the live deployment — every LLM call, node execution, and routing decision is fully auditable at smith.langchain.com under the project name script_approval_agent.
