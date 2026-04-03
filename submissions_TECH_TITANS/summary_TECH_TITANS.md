# Submission Summary

## Team

**Tech Titans:**  
**Members:** Seeya Agrawal | AI & Backend Developer (Agent Workflow Builder)
Sushree Mohanty |   Integration & Automation Engineer
Shreya R Nair | Integration & Automation Engineer
**Contact Email:** seeyaagrawal01@gmail.com  

---

## Problem Statement

**Selected Problem:** (PS-01)   
**Problem Title:** (Client Onboarding)  

The current onboarding process at Scrollhouse is manual, repetitive, and prone to human error. Each onboarding takes around 45 minutes and often results in missed steps such as incomplete Airtable entries or incorrect Notion templates. This leads to operational inefficiencies, delayed invoicing, and poor client experience. Automating this process ensures consistency, reduces errors, and significantly improves onboarding speed.

---

## System Overview

Our system automates the entire client onboarding process from start to finish. When a new client’s details are submitted through a simple form, the system automatically sends a welcome email, creates a structured Google Drive folder, generates a Notion client hub, and logs all client details in Airtable. Each step is executed sequentially without manual intervention, and a summary of all completed actions is returned. The system also logs every step for transparency and debugging. This reduces onboarding time from minutes to seconds while ensuring no steps are missed.

---

## Tools and Technologies

List every tool, library, framework, API, and model your system uses. For each one, state what it does in your system, not just what it is.

| Tool or Technology | Version or Provider | What It Does in Your System |
|FastAPI|Python Framework|Handles API requests and executes onboarding workflow|
| Python  | Programming Language  | Core Core backend logic and workflow execution |
|  HTML, CSS, Javascript | Core backend logic and workflow execution  |  Frontend UI for client data input |
| Uvicorn |	ASGI Server | Runs the FastAPI application locally|
|Pydantic | Python Library |	Validates input data structure |
| Logging (Custom)	|Python	| Tracks each step of the onboarding process|
| Simulated APIs | Local Mock	|Mimics Google Drive, Notion, Airtable, and Email services |

---

## LLM Usage

**Model(s) used:**Not implemented (designed for future integration)  
**Provider(s):**N/A 
**Access method:**N/A 

List every place in your system where an LLM is called. For each call, describe what the LLM receives as input, what decision or output it produces, and how that output affects the next step.

| Step | LLM Input | LLM Output | Effect on System |
|N/A|N/A|N/A|Current system is deterministic|
|   |   |   |   |
|   |   |   |   |

---

## Algorithms and Logic

The system follows a sequential workflow execution model where each step depends on the successful completion of the previous one. The backend validates input data before proceeding. Each service (email, drive, notion, airtable) is modular and independently executed.

Basic validation logic ensures incorrect inputs (e.g., invalid dates) are flagged early. Logging is implemented at each stage to track execution and detect failures. The system can be extended with retry logic and conditional branching for edge cases.
---

## Deterministic vs Agentic Breakdown

This section is verified. Do not overstate the agentic percentage. Judges have access to your code and will check.

**Estimated breakdown:**

| Layer | Percentage | Description |
| Deterministic automation |	85%	 |Fixed workflow execution, API calls, data validation, logging |
| LLM-driven and agentic	| 15% |	Designed for future decision-making (email personalization, validation, anomaly detection) | 


**Total must equal 100%.**

The current system is mostly deterministic, executing predefined steps in sequence. However, it is designed to incorporate agentic behavior where an LLM can make decisions such as handling ambiguous inputs, generating personalized emails, or detecting anomalies. Without an LLM, the system lacks adaptability and intelligent decision-making.

---

## Edge Cases Handled

List the edge cases from your problem statement that your system handles, and briefly describe the handling logic for each.

| Edge Case | How Your System Handles It |
| Invalid start date	| Validation stops execution and returns error |
| Missing input fields |	Pydantic validation prevents request processing |
| API/service failure (simulated)	|Logged for debugging |

Not implemented:

Duplicate brand detection (time constraint)
Real API failure retries
Email bounce handling

---

## Repository

**GitHub Repository Link:** https://github.com/seeya924/AgenticAI_DevSummit_2026 
**Branch submitted:** main  
**Commit timestamp of final submission:** (paste the exact commit hash and timestamp in UTC)  

The repository must be public at the time of submission. Private repositories will not be reviewed.

The repository must contain a README that explains how to run the system locally, including environment setup, required API keys, and a sample input to test with. If the README does not exist or is insufficient, the submission will be penalised.

---

## Deployment

**Is your system deployed?** No  

If yes:

**Deployment link:**  
**Platform used:** (Render / Railway / Hugging Face Spaces / Replit / other)  
**What can be tested at the link:**  

If no, this field can be left blank. Deployment is not required for evaluation but will be considered a positive signal.

---

## Known Limitations

Be honest. List anything your system does not handle, any edge cases you ran out of time to implement, any components that are mocked or hardcoded for the demo, and any known failure modes.

Judges will not penalise honest limitations. They will penalise limitations that were hidden and discovered during the demo.

---

## Anything Else

If there is anything about your system that is not captured in the sections above and that you want judges to know, include it here. This is optional.