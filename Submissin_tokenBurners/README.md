# ScriptAgent

**Content approval loop automation for Scrollhouse.**

An agentic system that tracks scripts through client approval, classifies informal responses using an LLM, sends follow-ups on schedule, and escalates when clients go silent — without anyone holding its hand.

---

## The problem

Scrollhouse manages 22 active clients. At any point, 8–15 scripts are somewhere in the approval loop. The team lead tracked all of it in their head. Scripts sat unseen for 5 days. One client approved via WhatsApp emoji and it was never actioned. The team lead spent 3–4 hours a week manually chasing responses.

The real problem wasn't the volume. It was that no system could read what clients actually say.

---

## What ScriptAgent does

1. Receives a script submission
2. Sends an approval request to the client (email or WhatsApp)
3. Waits for a response — checking at defined intervals
4. **Classifies the response using an LLM** — this is the core
5. Routes based on classification: approved → production queue, revisions → scriptwriter task, rejected → escalate
6. Sends follow-ups at 24h and 48h if no response
7. Escalates to the account manager at 72h with full history
8. Logs every action with timestamps

---

## Why the classifier matters

Most systems do this:

```python
if "approved" in response.lower():
    status = "approved"
```

This system does this:

```
"looks good 👍"              → approved
"🔥"                         → approved
"yes go ahead"               → approved
"almost, fix the hook"       → revisions
"can we jump on a call?"     → call_requested
"this doesn't work at all"   → rejected
"k"                          → approved (low confidence flagged)
```

The LLM reads what clients actually say, not what they're supposed to say.

---

## Architecture

```
POST /submit
      │
      ▼
┌─────────────────────────────────────┐
│           LangGraph Agent           │
│                                     │
│  send_approval_request              │
│        │                            │
│        ▼                            │
│  check_for_response ←──────────┐   │
│        │                       │   │
│   response? ──no──► followup ──┘   │
│        │                           │
│       yes                          │
│        ▼                           │
│  classify_response  (LLM call)     │
│        │                           │
│   ┌────┴────────────────────┐      │
│   │                         │      │
│ approved   revisions   rejected    │
│   │           │           │        │
│ update   extract_notes  escalate   │
│ tracker  → scriptwriter            │
└─────────────────────────────────────┘
```

**State travels through every node as a typed dict:**

```python
ScriptState:
  script_id, script_text, client_name
  client_contact, account_manager
  preferred_channel, sla_hours
  status, follow_up_count
  client_response, classification
  revision_notes, history, sent_at, version
```

---

## Tech stack

| Layer | Tool | Why |
|-------|------|-----|
| Agent graph | LangGraph | Stateful loop with conditional branching |
| LLM calls | LangChain + Claude (Anthropic) | Classification and revision extraction |
| API server | FastAPI | Receives submissions and responses |
| Persistence | SQLite | Zero-config state storage |
| Frontend | Vanilla HTML/CSS/JS | Single file, served statically |

---

## Project structure

```
scriptagent/
├── main.py           # FastAPI server — entry point
├── agent.py          # LangGraph graph — node wiring and edges
├── nodes.py          # All node functions
├── classifier.py     # LLM classification logic
├── database.py       # SQLite read/write helpers
├── mock_clients.py   # Demo data
├── static/
│   └── index.html    # Dashboard frontend
├── .env              # API key
└── requirements.txt
```

---

## Setup

```bash
# Clone and enter
git clone https://github.com/anxbt/scriptagent
cd scriptagent

# Install dependencies
pip install -r requirements.txt

# Add your Anthropic API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run
uvicorn main:app --reload
```

Open `http://localhost:8000` for the dashboard.

---

## API

### Submit a script
```bash
curl -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "SCR-001",
    "script_text": "Hook: Have you ever looked in the mirror and...",
    "client_name": "GlowSkin",
    "client_contact": "priya@glowskin.com",
    "account_manager": "Rohit",
    "preferred_channel": "email",
    "sla_hours": 48
  }'
```

### Simulate a client response
```bash
curl -X POST http://localhost:8000/respond \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "SCR-001",
    "response": "looks good 👍 send it"
  }'
```

### Check script status
```bash
curl http://localhost:8000/status/SCR-001
```

### View all active scripts
```bash
curl http://localhost:8000/dashboard
```

---

## Requirements

```
langgraph>=0.1.0
langchain>=0.2.0
langchain-anthropic>=0.1.0
fastapi>=0.110.0
uvicorn>=0.29.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

## The differentiator

Every team at this hackathon built a pipeline. This project focused on the one node that actually requires intelligence — reading what clients say, not what they're supposed to say.

A pipeline without a brain is a webhook with extra steps.

## Screenshots

**SMTP Server Emails:**
![SMTP Server Emails Placeholder](https://via.placeholder.com/800x400?text=Upload+SMTP+Email+Screenshot+Here)
*Upload the screenshot of the emails received from the SMTP server here.*

---

Built for **Developer's Summit 3.0 — Agentic AI Hackathon**
GDG On Campus · Silicon University · 3 Apr 2026