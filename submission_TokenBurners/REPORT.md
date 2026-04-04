# ScriptAgent Gemini Integration Report

## What changed

- The LLM provider was switched from Anthropic to Google's Gemini API.
- The app now reads `GEMINI_API_KEY`, `GEMINI_API_KEY_BACKUP`, and `GEMINI_MODEL` from `.env`.
- The classifier in `classifier.py` now:
  - tries Gemini first
  - falls back to the backup Gemini key if the first one fails
  - falls back to simple heuristics if Gemini is unavailable
- `requirements.txt` now installs `google-genai` instead of `langchain-anthropic`.

## How the app works

1. A script is submitted to `POST /submit`.
2. The LangGraph agent starts and runs `send_approval_request`.
3. The script is stored in SQLite with status `awaiting_response`.
4. A client reply is sent to `POST /respond`.
5. The agent runs again:
   - `check_for_response` sees the new reply
   - `classify_response` asks Gemini what the client meant
   - routing sends the script to the correct next step
6. Final states include:
   - `approved`
   - `needs_revision`
   - `call_requested`
   - `escalated`

## Why Gemini is used

- Gemini is handling the hard part of the product: informal client-language understanding.
- That means messages like `looks good 👍` or `can we jump on a call?` are interpreted by the model instead of fragile keyword matching.
- Revision extraction also uses Gemini to turn messy feedback into structured notes.

## Endpoints tested

### `GET /`
- Result: success
- Purpose: confirms the FastAPI app is running

### `GET /dashboard`
- Result: success
- Purpose: returns all scripts and their current states
- Verified statuses in the dashboard:
  - approved
  - needs_revision
  - call_requested
  - escalated
  - awaiting_response

### `POST /submit`
- Result: success
- Verified with fresh scripts:
  - `GEM-101`
  - `GEM-102`
  - `GEM-103`
- Purpose: creates a script row and sends the initial approval request

### `POST /respond`
- Result: success
- Tested three real response types:
  - `looks good 👍 send it` -> `approved`
  - `almost perfect but can you make the hook more punchy? also the CTA feels weak` -> `needs_revision`
  - `can we jump on a call?` -> `call_requested`

### `GET /status/{script_id}`
- Result: success
- Verified with `GET /status/GEM-103`
- Purpose: returns the latest stored state for one script

## Verified live outcomes

### Approval path
- Script ID: `GEM-101`
- Client response: `looks good 👍 send it`
- Result:
  - classification = `approved`
  - final status = `approved`
  - history shows move to production queue

### Revision path
- Script ID: `GEM-102`
- Client response: `almost perfect but can you make the hook more punchy? also the CTA feels weak`
- Result:
  - classification = `revisions`
  - final status = `needs_revision`
  - extracted notes:
    - `1. Make the hook more punchy [UNCLEAR].`
    - `2. Address the CTA as it "feels weak" [UNCLEAR].`

### Call request path
- Script ID: `GEM-103`
- Client response: `can we jump on a call?`
- Result:
  - classification = `call_requested`
  - final status = `call_requested`
  - history shows escalation to account manager for call scheduling

### Overdue escalation path
- Pre-seeded script: `DEMO-OVERDUE-001`
- Result:
  - startup poller escalated it automatically
  - final status = `escalated`

## Important implementation detail

- LangGraph only preserves keys declared in the state schema.
- A routing bug was fixed by adding `next_action` and `escalation_reason` to `ScriptState`.
- Without that fix, the graph stopped after `check_for_response` instead of continuing to follow-up or escalate.

## Current environment

- Python 3.11 is installed locally
- A virtual environment exists at `.venv`
- The app was run successfully with:

```bash
source .venv/bin/activate
uvicorn main:app --reload
```

## Security note

- The Gemini keys were placed into `.env` so the app could be wired and tested live.
- Because the keys were shared in chat, they should be treated as exposed and rotated after the demo.

## What you can say in the demo

> We built an approval-loop agent, not just a form pipeline.  
> The key step is the response-classification node, where Gemini reads what the client actually meant, including informal approvals, revision requests, and call requests.  
> That lets the system route each script automatically instead of relying on rigid keyword rules or a team lead remembering everything manually.
