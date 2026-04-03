# Submission Summary

## Team

**Team Name:** Agents

**Members:**

| Name | Role |
|---|---|
| Sridhar Sahu | Lead |
| Tinku Kumar Mahto | Member |
| Kanha Raheja | Member |

**Contact Email:** sahusridhar23@gmail.com

---

## Problem Statement

**Selected Problem:** PS-01
**Problem Title:** Client Onboarding

Scrollhouse account managers manually execute a four-step onboarding sequence for every new client — writing a welcome email, creating a Google Drive folder, setting up a Notion page, and adding a record to Airtable — taking 45 minutes per client and resulting in errors or missed steps in approximately 50% of onboardings. Incomplete Airtable entries delay invoices, wrong Notion templates disrupt the first week of communication, and three clients flagged onboarding issues in their first check-in calls in the past six months. Our system eliminates this entirely by delegating the full sequence to an AI agent, reducing the process to under 2 minutes with near-zero error rate.

---

## System Overview

When a new client is signed, their details (brand name, account manager, start date, billing contact, deliverable count, and invoice cycle) are submitted through a web form or API call. This triggers an AI agent — powered by Claude claude-opus-4-5 — that works through the onboarding sequence automatically: it sends a personalised welcome email to the client, creates a Google Drive folder with the correct five-subfolder structure and sets the right access permissions, builds a Notion client hub from the latest master template populated with the client's details and a first-month content calendar, and adds a fully populated record to the Airtable client tracker including links to the Drive folder and Notion page. Once all steps are complete, the agent emails the account manager a summary with direct links to all three tools and logs the full run with a timestamp and step-by-step audit trail. The account manager receives everything set up and linked — without touching a single tool themselves.

---

## Tools and Technologies

| Tool or Technology | Version or Provider | What It Does in Your System |
|---|---|---|
| Claude claude-opus-4-5 | Anthropic API | Main agent brain — orchestrates the full onboarding loop using Tool Use, decides which tools to call, passes outputs between steps, detects edge cases |
| Claude Haiku (claude-haiku-4-5) | Anthropic API | Generates personalised welcome email body copy for each client based on brand name, account manager, and start date |
| @anthropic-ai/sdk | v0.20.0 | Node.js SDK used to call the Anthropic API and run the agentic tool-use loop |
| Node.js + Express | v18+ / v4.18 | HTTP server that exposes the onboarding trigger endpoint and status/log endpoints |
| googleapis | v128.0.0 | Google Drive API client — creates the root folder and 5 subfolders, sets commenter access for client and editor access for account manager |
| Notion REST API | 2022-06-28 | Creates the client hub page under the parent workspace, always fetching the latest master template before creation |
| Airtable SDK | v0.12.2 | Checks for duplicate brand names before writing, then creates a fully populated client record with all 12 required fields |
| Nodemailer | v6.9.7 | SMTP email delivery for both the welcome email (to client) and the completion summary (to account manager) |
| dotenv | v16.3.1 | Loads all API keys and config from the .env file so no credentials are hardcoded |
| uuid | v9.0.0 | Generates a unique run ID for each onboarding execution for audit log tracking |
| HTML/CSS/JS (Vanilla) | — | Frontend dashboard — form for triggering onboardings, real-time agent console, step tracker, and run logs table |

---

## LLM Usage

**Model(s) used:** Claude claude-opus-4-5, Claude Haiku (claude-haiku-4-5)
**Provider(s):** Anthropic
**Access method:** API key (set in .env as `ANTHROPIC_API_KEY`)

| Step | LLM Input | LLM Output | Effect on System |
|---|---|---|---|
| 1. Agent orchestration (claude-opus-4-5) | System prompt describing the 8-step onboarding process + all client data (brand name, AM, start date, billing email, deliverable count, invoice cycle) + today's date | A sequence of tool_use calls in the correct order, with correct inputs derived from client data and outputs of earlier steps | Drives the entire execution — Claude decides which tool to call next, what parameters to pass, and whether to flag an issue. The loop runs until Claude signals end_turn |
| 2. Cross-step data passing (claude-opus-4-5) | Tool results from earlier steps (e.g. Drive shareLink, Notion pageUrl) returned as tool_result messages | Subsequent tool calls that include those links as parameters (e.g. drive_link and notion_link in the Airtable tool call) | Ensures Airtable record always contains both links — this was the most common failure in the manual process |
| 3. Edge case detection (claude-opus-4-5) | Client data including contract_start_date compared against today's date injected into the system prompt | Calls to flag_issue tool with appropriate issue_type (retroactive_date, unknown_account_manager, duplicate_brand, etc.) | Halts or warns before creating bad records — no downstream corruption from bad input |
| 4. Email copy generation (claude-haiku-4-5) | Prompt containing brand name, account manager name, contract start date, and calendar link | A 150–200 word personalised welcome email body in a warm, human tone | Replaces the templated email approach — each client receives unique copy written for their specific context |

---

## Algorithms and Logic

### Agentic Tool-Use Loop

The core of the system is a `while` loop in `onboardingAgent.js` that runs up to 20 iterations. Each iteration sends the current message history (including all prior tool results) to Claude claude-opus-4-5. If Claude returns `stop_reason: tool_use`, the system iterates over all `tool_use` blocks in the response, executes each tool, and appends a `tool_result` message back into the conversation history. This continues until Claude returns `stop_reason: end_turn`, signalling it is satisfied the onboarding is complete.

### Tool Selection Logic

Claude selects tools based on the system prompt's instructions and the current state of the conversation. It is instructed to follow a specific order (email → drive → notion → airtable → summary) but decides autonomously how to handle deviations — for example, if a drive tool call returns an error, Claude calls `flag_issue` and then continues to the next step rather than aborting the run. This is a deliberate design choice: partial completion with a flagged error is better than a full failure that leaves nothing done.

### Cross-Step Output Passing

Claude extracts outputs from tool results (e.g. `shareLink` from the Drive step, `pageUrl` from the Notion step) and uses them as inputs to later tool calls. This is not hardcoded — Claude reads the tool result JSON and constructs the next tool call's parameters from it. The system also caches these values in a `context.results` object server-side as a safety net.

### Duplicate Check

Before the Airtable record is created, `checkDuplicateBrand()` runs a case-insensitive filter query against the Airtable base. If a matching record exists, the tool returns `{ duplicate: true }` instead of writing, and Claude calls `flag_issue(duplicate_brand)`.

### Content Calendar Generation

`generateContentCalendar()` is a deterministic function that spreads `deliverable_count` items across 4 weeks starting from the contract start date, cycling through 12 content type labels. It returns a structured array that is passed directly into the Notion page creation call.

### Retry Logic

Each tool call is wrapped in a try/catch. On failure, the error is returned as the tool result. Claude is instructed in the system prompt to attempt a retry by calling the same tool again if it receives an error response, and to call `flag_issue(api_failure)` if the second attempt also fails.

---

## Deterministic vs Agentic Breakdown

| Layer | Percentage | Description |
|---|---|---|
| Deterministic automation | 30% | HTTP request handling, input validation, Google Drive folder creation and permission setting, Airtable duplicate query, content calendar date calculation, SMTP email delivery, run logging and timestamping |
| LLM-driven and agentic | 70% | Tool selection and sequencing, cross-step parameter extraction, edge case detection and flagging, retry decisions, email copy generation, determining when the onboarding is complete |

If the LLM were replaced with a fixed script, the system would lose the ability to handle unexpected inputs gracefully — a fixed script cannot detect that an account manager name is missing or that a start date is retroactive; it would either crash or silently create a bad record. It would also lose the ability to pass Drive and Notion links into the Airtable call dynamically, since a script would need those values hardcoded or returned via a rigid pipeline with no tolerance for step failures. The personalised email copy would revert to a static template. Most importantly, the current system can recover from partial failures and continue — a fixed script with the same integrations would be all-or-nothing.

---

## Edge Cases Handled

| Edge Case | How Your System Handles It |
|---|---|
| Email bounce / delivery failure | SMTP error is caught, returned as tool result, Claude calls `flag_issue(email_bounce, severity: blocking)`, welcome email step is marked failed, account manager is alerted in the completion summary |
| Duplicate brand name in Airtable | `checkDuplicateBrand()` runs a case-insensitive filter before every write. If a match is found, tool returns `{ duplicate: true }` and Claude calls `flag_issue(duplicate_brand)` — no duplicate record is created |
| Contract start date in the past | Today's date is injected into the system prompt. Claude compares start date to today and calls `flag_issue(retroactive_date, severity: warning)` before proceeding — the onboarding continues but the flag is logged and included in the AM summary |
| Unknown or missing account manager email | If `account_manager_email` is missing or flagged as unknown, Claude calls `flag_issue(unknown_account_manager, severity: blocking)` — Drive permissions and completion summary cannot be sent without a valid AM email |
| Google Drive API failure | try/catch on the tool executor returns the error to Claude as a tool result. Claude retries once; if it fails again, `flag_issue(api_failure)` is called and the AM receives manual setup instructions in the completion summary |
| Wrong or cached Notion template | The Notion service always fetches the live template page from the API on every run before creating the new page — there is no local caching of template content |

**Edge cases not implemented (due to time):**

| Edge Case | Reason Not Implemented |
|---|---|
| Webhook signature verification | The trigger endpoint accepts any POST — in production, the `WEBHOOK_SECRET` env var would be used to verify HMAC signatures on incoming webhooks from the CRM. Skipped to keep the demo setup simple |
| Persistent log storage | Onboarding logs are stored in `global.onboardingLogs` in memory and are lost on server restart. A production system would write to a database |
| Email bounce detection via webhook | The current implementation catches SMTP send failures, but does not handle async bounce notifications that email providers send back hours later via webhook |

---

## Repository

**GitHub Repository Link:** *(push your code to GitHub and paste the URL here)*
**Branch submitted:** main
**Commit timestamp of final submission:** *(paste exact commit hash and UTC timestamp after final push)*

The repository contains a README explaining local setup, required environment variables, and a sample curl command to test the onboarding trigger.

---

## Deployment

**Is your system deployed?** No

The system runs locally via `npm run dev` in the `backend/` directory. The frontend is a single HTML file opened directly in the browser. No cloud deployment was completed within the hackathon window.

---

## Known Limitations

- **API keys required for full functionality.** Without valid Anthropic, Google, Notion, Airtable, and SMTP credentials in `.env`, the agent will fail at each integration step. The dashboard UI and demo simulation run without keys, but the real tool calls will not execute.
- **In-memory log storage.** All run logs are lost on server restart. A production version would persist to a database.
- **No auth on the trigger endpoint.** Any POST to `/api/onboarding/trigger` will execute — there is no API key or session check on the endpoint itself.
- **Content calendar is deterministic only.** The first-month content calendar assigned to each client cycles through 12 fixed content types in order. A production version would use Claude to generate a more contextually appropriate calendar based on brand category.
- **Email bounce detection is synchronous only.** We detect send failures at the SMTP level but do not handle asynchronous delivery failure notifications (bouncebacks that arrive minutes or hours later from the recipient mail server).
- **Google OAuth refresh token setup is manual.** Getting the initial refresh token requires running through the OAuth playground once — this is documented in the README but adds setup friction.
- **No test suite.** There are no automated tests. All validation was done manually during development.

---

## Anything Else

The most important design decision in this project was using Claude's **Tool Use** in a genuine agentic loop rather than building a sequential script that calls Claude once for email copy and then hard-codes everything else. This means the system is resilient to changes — if a new step is added to the onboarding process, it can be described as a new tool and Claude will incorporate it into the sequence without any changes to the orchestration logic. The same architecture that handles 6 tools today can handle 12 tomorrow.

The dual-model approach (claude-opus-4-5 for orchestration, claude-haiku-4-5 for email generation) is a deliberate cost/capability trade-off: Opus handles the complex multi-step reasoning and tool selection, while Haiku handles the single-turn creative writing task where its speed and lower cost are advantages.
