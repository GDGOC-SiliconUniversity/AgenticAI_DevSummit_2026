# AgenticAI DevSummit 2026

**Original Source Code**: [https://github.com/anxbt/silicon-hackathon](https://github.com/anxbt/silicon-hackathon)

Agentic workflow implementation for the Content Approval Loop case (PS-03).

This repository contains one full submission in submission_TokenBurners. The system automates script approval follow-ups, response classification, revision extraction, and escalation using FastAPI, LangGraph, SQLite, Gemini, and a React dashboard.

## Problem Solved

Manual client approval tracking causes missed follow-ups, delayed production, and poor visibility.

This project automates the loop:

1. Send script approval request to client.
2. Monitor for response.
3. Follow up at 24h and 48h.
4. Escalate at 72h if no response.
5. Classify client replies (approved / revisions / rejected / call requested).
6. Route to final state and keep a complete audit trail.

## Repository Layout

- submission_TokenBurners/: Main implementation.
- Problem_Statement.md: Hackathon problem statements.
- EVALUATION.md: Scoring and judging criteria.
- RULES.md: Event and submission rules.
- SUBMISSIONS.md: Team submission instructions.

## Submission Architecture

### High-level components

1. API layer (FastAPI)
- Entry point: submission_TokenBurners/main.py
- Exposes endpoints for submit/respond/status/dashboard/health.
- Starts a background poller for periodic agent sweeps.

2. Agent orchestration (LangGraph)
- Graph builder: submission_TokenBurners/agent.py
- Nodes + routing logic: submission_TokenBurners/nodes.py
- Stateful loop with conditional transitions.

3. Persistence (SQLite)
- DB module: submission_TokenBurners/database.py
- Stores lifecycle state, history, versioning, classification, and timestamps.

4. Intelligence layer (Gemini + heuristics fallback)
- Classifier module: submission_TokenBurners/classifier.py
- Interprets informal client replies.
- Extracts revision notes from unstructured text.

5. Delivery channel
- Email integration: submission_TokenBurners/email_service.py
- Uses Resend when preferred_channel is email.

6. Frontend dashboard (React + Vite)
- App root: submission_TokenBurners/frontend/src/app/App.tsx
- Polling hook: submission_TokenBurners/frontend/src/features/dashboard/hooks/useScriptDashboard.ts
- Shows health, queue, statuses, and script details.

## Agent State Flow

Core graph path:

1. START -> send_approval_request (for new/pending scripts)
2. send_approval_request -> END
3. START -> check_for_response (for active scripts)
4. check_for_response routes to:
- classify_response (new reply)
- send_followup (24h/48h reminders)
- escalate (72h no reply)
- wait (no action)
5. classify_response routes to:
- update_tracker (approved)
- extract_revision_notes (revisions)
- escalate (rejected/call requested)
- send_followup (unclear)

Final statuses include approved, needs_revision, rejected, call_requested, and escalated.

## API Contract

Base URL: http://127.0.0.1:8000

1. GET /
- Health response.

2. POST /submit
- Creates or resubmits a script and runs the agent immediately.
- Required payload:
	- script_id
	- script_text
	- client_name
	- client_contact
	- account_manager
	- preferred_channel (email | whatsapp)
	- sla_hours (optional, default 48)

3. POST /respond
- Stores client response and re-runs the agent for routing.
- Payload:
	- script_id
	- response

4. GET /status/{script_id}
- Returns latest state for one script.

5. GET /dashboard
- Returns all scripts for dashboard display.

## Local Setup

Requirements:

- macOS/Linux/WSL
- Python 3.11+
- Node.js 18+
- npm

### 1. Clone and enter submission

```bash
cd AgenticAI_DevSummit_2026/submission_TokenBurners
```

### 2. Create Python environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create submission_TokenBurners/.env:

```env
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEY_BACKUP=your_backup_key
GEMINI_MODEL=gemini-2.5-flash

DATABASE_PATH=scriptagent.db
POLL_INTERVAL_SECONDS=10

RESEND_API_KEY=your_resend_key
RESEND_FROM_EMAIL=ScriptAgent <onboarding@resend.dev>
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Running the App

### Option A: One command for backend + frontend

```bash
./start_demo.sh
```

Starts:

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

### Option B: Run services separately

Backend:

```bash
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend (new terminal):

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

## Quick Demo Walkthrough

1. Open dashboard at http://127.0.0.1:5173.
2. Submit a script with preferred_channel as email or whatsapp.
3. Observe status transition to awaiting_response.
4. Send a reply through POST /respond, examples:
- looks good 👍
- can you revise the hook and CTA?
- can we jump on a call?
5. Confirm status transition:
- approved
- needs_revision
- call_requested
6. Inspect history timeline in dashboard and status API.

## cURL Examples

Submit script:

```bash
curl -X POST http://127.0.0.1:8000/submit \
	-H "Content-Type: application/json" \
	-d '{
		"script_id": "DEMO-900",
		"script_text": "New product launch script",
		"client_name": "Acme",
		"client_contact": "client@example.com",
		"account_manager": "Riya",
		"preferred_channel": "email",
		"sla_hours": 48
	}'
```

Respond to script:

```bash
curl -X POST http://127.0.0.1:8000/respond \
	-H "Content-Type: application/json" \
	-d '{
		"script_id": "DEMO-900",
		"response": "Looks good, approved"
	}'
```

Fetch dashboard:

```bash
curl http://127.0.0.1:8000/dashboard
```

## Judge-Facing Notes

1. Agentic decision points are explicit in graph routing.
2. Every transition writes traceable history.
3. The system supports resubmission versioning.
4. Poll-based automation demonstrates unattended progress.
5. Edge cases covered in implementation:
- unclear replies -> clarification follow-up
- no response -> timed follow-ups and escalation
- rejected/call requested -> escalation flow

## Testing Checklist

1. Backend health endpoint returns 200.
2. New submission creates pending_send then awaiting_response state.
3. Approved response sets status to approved.
4. Revision response sets status to needs_revision with extracted notes.
5. Call-request response sets status to call_requested and escalates.
6. Dashboard updates reflect backend state.

## Troubleshooting

1. Module import errors
- Ensure virtual environment is active.
- Reinstall with pip install -r requirements.txt.

2. Gemini classification not working
- Check GEMINI_API_KEY in .env.
- Ensure outbound internet/API access.

3. Email send fails
- Check RESEND_API_KEY and RESEND_FROM_EMAIL.
- Confirm recipient and sender are valid for your Resend setup.

4. Port already in use
- Change ports in uvicorn or frontend command.

5. Frontend cannot reach backend
- Verify backend URL in VITE_API_BASE_URL or default http://127.0.0.1:8000.

## Security

Do not commit real API keys. If any key has been exposed in local files, rotate it immediately.

## License

This repository is for the Agentic AI DevSummit hackathon submission/demo use.
