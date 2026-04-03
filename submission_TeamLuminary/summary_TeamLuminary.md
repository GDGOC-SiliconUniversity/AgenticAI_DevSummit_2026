# Submission Summary

## Team

**Team Name:** Team Luminary  
**Members:**  
- Jagan Kumar Swain | Orchestration
- Ratish Ranjan Sahu | Triggering and Edge Case Handling 
**Contact Email:** *jagan.swain.ece.2024@nist.edu

---

## Problem Statement

**Selected Problem:** PS-02  
**Problem Title:** Content Brief to Script Pipeline

Scrollhouse's content coordinators spend 20–30 minutes manually rewriting each client brief into the internal format, and there is a 4–6 hour lag between a brief being submitted and the scriptwriter receiving it. Our system eliminates that lag entirely — from the moment a client submits a Google Form, the agent reads the brief, validates it, retrieves brand context, rewrites it into the internal creative format, creates the Notion page, notifies the scriptwriter on Slack, and logs everything in Airtable without any human in the loop.

---

## System Overview

A client submits a content brief via Google Forms, which populates a Google Sheet. The agent polls the sheet every 30 seconds. When a new row is found, it passes through a four-node LangGraph pipeline: the Parser node uses an LLM to validate whether the brief is complete and meaningful; the Brand Retriever uses FAISS vector search to pull tone-of-voice guidelines and client rules from the brand knowledge base; the Interpreter uses an LLM to generate hook options (ranked by strength), tone direction, visual treatment suggestions, and a confidence score; and the Dispatcher creates a formatted Notion brief page, sends a Slack notification to the assigned scriptwriter with a deadline, and updates the Airtable tracker. If the brief is incomplete or ambiguous, the agent flags it and notifies the coordinator instead of the scriptwriter.

---

## Tools and Technologies

| Tool or Technology | Version or Provider | What It Does in Your System |
|---|---|---|
| Python | 3.13 | Core runtime |
| LangGraph | latest | Stateful 4-node agent pipeline with conditional routing |
| LangChain | latest | Prompt management and LLM chain construction |
| langchain-google-genai | latest | Gemini API integration for LangChain |
| Google Gemini 2.5 Flash | Google AI Studio | LLM for brief parsing and creative interpretation |
| FAISS (faiss-cpu) | latest | Vector similarity search for brand context retrieval |
| sentence-transformers (all-MiniLM-L6-v2) | Hugging Face | Embedding model for brand name → brand profile matching |
| Notion API (notion-client) | latest | Creates formatted brief pages for scriptwriters |
| Slack Incoming Webhooks | Slack | Notifies scriptwriters and coordinator with brief summary and Notion link |
| Airtable REST API | Airtable | Tracks brief status, scriptwriter assignment, and Notion link |
| Google Sheets API (google-api-python-client) | Google | Polls for new brief submissions |
| python-dotenv | latest | Environment variable management |
| Pydantic | v2 | Typed data models for all agent state objects |

---

## LLM Usage

**Model(s) used:** gemini-2.5-flash  
**Provider(s):** Google AI Studio  
**Access method:** API key via `GOOGLE_API_KEY` environment variable

| Step | LLM Input | LLM Output | Effect on System |
|---|---|---|---|
| Parser (Node 1) | All 8 brief fields (brand name, content type, topic, key message, target audience, mandatory inclusions, reference URLs, notes) | JSON: `{ "is_complete": bool, "missing_fields": [str] }` | If `is_complete` is false, the pipeline branches to the dispatcher with `flagged=True`. The brief never reaches the interpreter. |
| Interpreter (Node 3) | Validated brief fields + brand context (tone of voice, past themes, client rules from FAISS) | JSON: `{ "hook_options": [3 strings], "tone_direction": str, "visual_treatment": str, "scriptwriter_notes": str, "one_line_summary": str, "ambiguity_flags": [str], "confidence_score": float }` | If `confidence_score < 0.70`, the pipeline flags the brief. If confident, the interpreted brief is passed to the dispatcher for Notion page creation and Slack notification. |

---

## Algorithms and Logic

**FAISS Brand Retrieval (RAG):**  
Each brand profile in `data/brand_profiles.json` is embedded at index-build time using `all-MiniLM-L6-v2` (384-dimensional vectors, L2 index). At runtime, the submitted brand name is embedded and the nearest neighbour is retrieved. If the L2 distance exceeds the threshold (1.2), the brand is considered unrecognised and the brief is flagged. This allows fuzzy brand name matching — minor typos will still retrieve the correct brand.

**LangGraph Routing:**  
After every node except the dispatcher, a `should_continue` function checks `state.flagged`. Any node can flag the state. Once flagged, the graph short-circuits to the dispatcher, which handles the flagged path (coordinator alert + "Flagged" Airtable status) instead of the happy path.

**Confidence Gating:**  
The interpreter returns a `confidence_score` float. If below 0.70, the brief is treated as ambiguous — the interpreted brief is still attached to the state (for reference), but the pipeline routes to the flagged dispatcher path.

**Scriptwriter Assignment:**  
Reads `data/scriptwriters.json`. Skips writers with `"on_leave": true`. Assigns the first available writer. Includes a "Backup Writer" as the last-resort fallback.

**Deduplication:**  
Processed row IDs are written to `data/processed_rows.json` after each fetch. The agent will never reprocess the same sheet row.

---

## Deterministic vs Agentic Breakdown

**Estimated breakdown:**

| Layer | Percentage | Description |
|---|---|---|
| Deterministic automation | 35% | Google Sheets polling and row deduplication; FAISS index lookup and distance threshold check; Notion page construction from template; Slack webhook POST; Airtable API calls; scriptwriter roster lookup |
| LLM-driven and agentic | 65% | **Parser:** LLM reads all 8 brief fields and classifies whether the submission is complete and meaningful — it catches semantic meaninglessness ("tbd", "idk", "???") not just blank fields. **Interpreter:** LLM reads the validated brief plus brand context and generates the entire internal brief — hooks, tone, visual direction, scriptwriter notes, and a confidence score that gates whether the brief proceeds or is flagged. |

Remove the LLM from the parser and any submission — no matter how incomplete or nonsensical — passes through to the scriptwriter. Remove the LLM from the interpreter and there is no internal brief: the scriptwriter would receive the raw client form response, which is exactly the problem this system was built to eliminate.

---

## Edge Cases Handled

| Edge Case | How Your System Handles It |
|---|---|
| Critical fields left blank | Parser LLM flags `is_complete: false` and lists the missing fields. Pipeline branches to coordinator alert. Brief is logged in Airtable as "Flagged". |
| Meaningless content ("tbd", "idk", "???", "n/a") | Parser LLM classifies these as incomplete — not just syntactically empty but semantically useless. Flagged identically to blank fields. |
| Unrecognised brand name | FAISS L2 distance exceeds threshold (1.2). State is flagged with message: "Unrecognised brand — possible new client or data entry error." |
| Assigned scriptwriter is on leave | `scriptwriters.json` filters out `on_leave: true` writers. First available writer is assigned. Backup Writer is always on_leave: false as fallback. |
| LLM returns malformed JSON | Both parser and interpreter catch `json.JSONDecodeError` and flag the brief for manual review rather than crashing. |
| Pipeline crash on any brief | `main.py` wraps `pipeline.invoke()` in a try/except. On crash, a Slack error alert is sent and the polling loop continues to the next brief. |
| Two briefs from same client simultaneously | Each brief is a separate sheet row with a unique `row_id`. They are processed independently. Separate Airtable records are created. No state is shared between them. |

**Edge cases not implemented (known limitations):**

| Edge Case | Reason |
|---|---|
| Broken reference URL | No HTTP validation implemented. URL is passed through to Notion as-is. |
| New content type for this client | Brand profiles do not store past content types. No precedent check exists. |
| Scriptwriter reassignment not explicitly logged | Airtable and Slack do not currently note whether a backup writer was assigned due to leave. |

---

## Repository

**GitHub Repository Link:** https://github.com/JaganKSwain/BriefParser 
**Branch submitted:** main  
**Commit timestamp of final submission:** 2026-04-03 16:47:00+05:30

The repository is public. The README contains full setup instructions, environment variable reference, and a sample test input.

---

## Deployment

**Is your system deployed?** No  

The system runs locally via `python main.py`. It polls Google Sheets every 30 seconds and processes new rows end-to-end without manual intervention. A judge can clone the repository, set up `.env`, run `python run_once/smoke_test.py` to verify credentials, and then run `python main.py` with a row pre-populated in the sheet.

---

## Known Limitations

- **No webhook trigger:** The agent uses polling (30-second interval) rather than a Google Forms webhook. New briefs have up to a 30-second pickup delay.
- **No broken URL validation:** Reference content URLs are passed through to Notion without checking if they are reachable.
- **No content type precedent check:** If a client submits a brief for a content type they have never done before (e.g., a long-form video), the agent does not flag this.
- **Notion pages not linked to per-client hubs:** All brief pages are created under a single parent page (`NOTION_PARENT_PAGE_ID`), not under individual client hub pages.
- **Scriptwriter speciality matching not implemented:** Assignment is "first available" — brand category and scriptwriter speciality are not matched.
- **Reassignment not logged:** If a brief is redirected to a backup writer because the primary is on leave, this is not explicitly noted in Airtable or the Slack message.

---

## Anything Else

The system was designed with honest boundaries between its deterministic and agentic layers. Every LLM call produces a JSON output that gates a real pipeline decision — incomplete briefs are never silently passed through, and low-confidence interpretations are never silently sent to scriptwriters. The FAISS retrieval step adds semantic resilience: a client who misspells their own brand name in the form will still match the correct brand profile, provided the edit distance is within the L2 threshold.

The test suite (`run_once/`) covers every individual node and the full end-to-end graph. Judges can verify each component independently before running the full pipeline.
