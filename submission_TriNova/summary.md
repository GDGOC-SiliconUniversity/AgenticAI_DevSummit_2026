# Submission Summary

## Team

Team Name: TriNova

Members:
Amrit Gourav Ray | Developer & Backend
Swayam Kumar Panda | AI Logic & LLM Integration
Anwesha Dash | UI & Testing

Contact Email: [amritray43@gmail.com](mailto:amritray43@gmail.com)

---

## Problem Statement

Selected Problem: PS-01
Problem Title: Client Onboarding

Scrollhouse currently performs client onboarding manually, taking ~45 minutes per client and often missing critical steps like data entry or incorrect setup. This leads to operational inefficiencies, delayed invoicing, and poor client experience.

Our system automates the entire onboarding workflow, reducing time to under 1 minute and minimizing human error.

---

## System Overview

Our system is an Agentic AI onboarding assistant that takes client details as input and completes onboarding automatically.

It uses an LLM to dynamically plan onboarding steps and executes them through multiple agents such as email sending, folder creation, and data storage.

The system ensures consistency, reduces errors, and generates a final onboarding summary without manual intervention.

---

## Tools and Technologies

| Tool or Technology | Version or Provider | Role in System     |
| ------------------ | ------------------- | ------------------ |
| Python             | 3.x                 | Core backend logic |
| Streamlit          | Latest              | UI for interaction |
| Groq API           | LLaMA3-70B          | LLM planning       |
| dotenv             | python-dotenv       | API key management |
| SMTP               | Gmail               | Email automation   |
| CSV                | Built-in            | Data storage       |

---

## LLM Usage

Model Used: LLaMA3-70B
Provider: Groq
Access Method: API Key

| Step     | Input          | Output               | Effect                    |
| -------- | -------------- | -------------------- | ------------------------- |
| Planning | Client details | Python list of steps | Dynamic workflow creation |
| Fallback | Same input     | Default steps        | Ensures reliability       |

---

## Algorithms and Logic

* LLM-based planner generates onboarding workflow dynamically
* Orchestrator maps steps to agent functions
* Sequential execution of tasks
* Retry logic for email sending
* Fallback plan if LLM fails

---

## Deterministic vs Agentic Breakdown

| Layer         | Percentage | Description                |
| ------------- | ---------- | -------------------------- |
| Deterministic | 70%        | Email, folder, CSV storage |
| Agentic       | 30%        | LLM-based planning         |

Without LLM, the system becomes static and loses adaptability.

---

## Edge Cases Handled

| Edge Case        | Handling         |
| ---------------- | ---------------- |
| Duplicate client | Blocks execution |
| Missing email    | Stops process    |
| Email failure    | Retry mechanism  |

---

## Repository

GitHub Repository: https://github.com/amritxcode/AgenticAI_DevSummit_2026
Branch: main
Final Commit Timestamp: 10:53 PM
---

## Deployment

Status: Not deployed

---

## Known Limitations

* Notion, Airtable, and Drive are simulated integrations
* Limited edge case handling
* No real external API integrations

---

## Improvements and Highlights

* Converted static automation to Agentic AI system
* LLM-driven workflow planning
* Multi-agent orchestration
* Retry logic for reliability

This system demonstrates how AI agents can automate real-world business workflows efficiently.
