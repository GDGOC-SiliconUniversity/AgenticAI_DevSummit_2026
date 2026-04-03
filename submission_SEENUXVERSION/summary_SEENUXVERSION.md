# Submission Summary

## Team
**Team Name:** SEENUX VERSION
**Members:** [Insert Your Name] | Lead Architect
[Insert Member Name] | AI Workflow Engineer
[Insert Member Name] | Documentation Specialist
**Contact Email:** [Insert Your Email Address]

---

## Problem Statement
**Selected Problem:** PS-01
**Problem Title:** Client Onboarding

This system addresses the 50% error rate and 45-minute manual drain associated with onboarding new brands at Scrollhouse. By automating folder creation, CRM syncing, and communication, it prevents delayed invoicing and eliminates the "unstructured" first impression that has previously risked client retention.

---

## System Overview
The Scrollhouse Autopilot System (SAS) is an end-to-end agentic workflow that triggers immediately upon a new client sign-up. It automatically builds a structured Google Drive environment, clones and populates a custom Notion Client Hub, and ensures 100% data integrity in Airtable. Beyond simple syncing, the system uses an AI agent to draft personalized welcome emails and generate a proactive first-month content strategy, ensuring the account manager can focus on the relationship rather than the setup.

---

## Tools and Technologies

| Tool or Technology | Version or Provider | What It Does in Your System |
|---|---|---|
| Gemini 1.5 Pro | Google AI Studio | Primary reasoning engine for edge-case handling and content generation. |
| LangGraph | LangChain | Orchestration framework managing stateful loops and retry logic. |
| n8n | Railway | Workflow automation connecting Drive, Notion, and Airtable APIs. |
| Pinecone | Vector Database | Stores latest master templates and brand voice guidelines. |
| Airtable API | REST API | Primary database for client records and project tracking. |

---

## LLM Usage
**Model(s) used:** Gemini 1.5 Pro
**Provider(s):** Google
**Access method:** API Key

| Step | LLM Input | LLM Output | Effect on System |
|---|---|---|---|
| Data Validation | Raw CRM Form Data | JSON validation / Error flags | Pauses workflow if manager name is unknown or date is in the past. |
| Content Strategy | Brand Category + Deliverables | 5 Content Pillars | Injects creative ideas into the Notion Hub before AM review. |
| Error Recovery | API Error Code + Context | Recovery Action (Retry/Alert) | Decides whether to re-attempt a Drive creation or notify the human AM. |

---

## Algorithms and Logic
We implemented a **Stateful Graph** using LangGraph. The system maintains a "State Object" that is updated at every node. 
- **Fuzzy Matching:** The LLM performs a semantic search on the Airtable database to detect duplicate brands even if the spelling differs slightly.
- **RAG Strategy:** We use a simple RAG pattern to pull the "Latest Master Template" ID from a vector store, ensuring the agent never uses an outdated Notion structure.

---

## Deterministic vs Agentic Breakdown

**Estimated breakdown:**

| Layer | Percentage | Description |
|---|---|---|
| Deterministic automation | 40% | Webhook triggers, folder structure creation, and basic field mapping into Airtable. |
| LLM-driven and agentic | 60% | Handling edge cases (duplicates/mismatches), generating content strategy, and self-healing error loops. |

**Total: 100%**

The agentic layer is critical for handling non-standard inputs. If replaced with a fixed script, the system would create duplicate records for similar brand names and fail to provide the "Content Strategy" value-add that differentiates Scrollhouse from competitors.

---

## Edge Cases Handled

| Edge Case | How Your System Handles It |
|---|---|
| Duplicate Brand Name | Agent flags the similarity and pauses the workflow for human confirmation. |
| Drive API Failure | Logs the error, waits 30 seconds, and retries. If failure persists, it alerts the AM. |
| Mismatched AM Name | Checks name against the internal staff directory and suggests the closest match. |

---

## Repository
**GitHub Repository Link:** [PASTE YOUR FORK LINK HERE]
**Branch submitted:** main
**Commit timestamp of final submission:** [PASTE YOUR COMMIT HASH HERE] 2026-04-03 14:15 UTC

---

## Deployment
**Is your system deployed?** Yes
**Deployment link:** https://seenux-repo-onboarding.railway.app
**Platform used:** Railway
**What can be tested at the link:** You can view the live execution logs and the status dashboard.

---

## Known Limitations
The current system does not automatically "re-try" the Notion creation if the Notion API itself is down for maintenance; it currently logs this as a failure for manual intervention.

---

## Anything Else
The "SEENUX VERSION" implementation includes a "Content Bonus" feature where the LLM creates five creative video hooks based on the brand's category, adding immediate value to the client's new Notion workspace.
