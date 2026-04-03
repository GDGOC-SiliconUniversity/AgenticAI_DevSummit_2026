# Submission Guide
### Agentic AI Hackathon | 3rd April

---

## How to Submit

Submissions happen via a fork of the official hackathon repository. Do not email files. Do not share Google Drive links. The fork is the only accepted submission format.

**Step 1.** Fork the official hackathon repository to your own GitHub account.

**Step 2.** Inside the forked repository, create a folder at the root level named exactly as follows:

```
submission_TEAMNAME
```

Replace TEAMNAME with your team's name. No spaces. No special characters. If your team name is "The Builders", the folder is `submission_TheBuilders`. Get this right. Folders named incorrectly will not be reviewed.

**Step 3.** Place exactly two files inside that folder. Nothing else. No subfolders, no extra assets, no zip files.

**Step 4.** Open a pull request from your fork back to the main repository before the submission deadline. The pull request timestamp is your official submission time. Anything pushed after the deadline will not be considered, even if the PR was opened before it.

---

## File 1: Presentation Deck

**Filename:** `presentation_TEAMNAME.pptx` or `presentation_TEAMNAME.pdf`

This is your demo deck. It should be self-contained, meaning someone who was not in the room should be able to understand what you built just by reading through it. You will also walk through this during your live demo, so structure it as something you can speak to, not just read off.

Your deck must cover the following, in roughly this order:

**The problem you picked.** Which problem statement (PS-01 through PS-04) did you work on, and what is the specific operational failure you are solving for? State the business cost of the problem in one or two lines. This is already documented in the case study, use it.

**Your system architecture.** A visual diagram of how your system works end to end. Every major component must be labeled: what triggers the agent, what tools it calls, what the LLM is responsible for deciding, where data flows in and where output flows out. If your diagram cannot be read without explanation, redraw it.

**Where the LLM makes decisions.** Explicitly mark on your architecture diagram or on a separate slide which steps are LLM-driven. What is the LLM reading, what decision is it making, and what happens as a result of that decision? This is not optional. Judges will ask about every node you mark.

**The agentic loop.** Show the reasoning and action cycle. What does one full loop look like: input received, LLM reads it, tool called, result evaluated, next action decided. Walk through this for a real input, not a hypothetical.

**Edge cases handled.** Pick at least two edge cases from your problem statement and show what your system does when they occur. Screenshots, logs, or a recorded walkthrough are all acceptable.

**What is automated vs what is agentic.** Be honest about this. A slide that clearly distinguishes your deterministic automation layer from your LLM-driven decision layer will be received better than one that calls everything "AI-powered."

**Live demo or recorded walkthrough.** If you are demoing live, this is your moment. If anything is likely to fail live, record a clean walkthrough and embed it or link it. A working demo from yesterday beats a broken demo today.

Slide count is not judged. Clarity is.

---

## File 2: Submission Summary

**Filename:** `summary_TEAMNAME.md`

This is a structured markdown document. Fill in every section. Do not leave fields blank. Do not write "N/A" unless it is genuinely not applicable. Judges will cross-reference this document against your code and your demo. Inconsistencies will be flagged.

Use the template below exactly. Do not rename sections.

---

```markdown
# Submission Summary

## Team

**Team Name:**  
**Members:** (Name | Role for each member, one per line)  
**Contact Email:**  

---

## Problem Statement

**Selected Problem:** (PS-01 / PS-02 / PS-03 / PS-04)  
**Problem Title:** (e.g., Client Onboarding / Content Brief to Script Pipeline)  

In two to four sentences, describe the specific operational failure your system addresses and what the business impact of solving it is.

---

## System Overview

In plain language, describe what your system does end to end. No jargon. Assume the reader is an operations manager at Scrollhouse, not an engineer. This should be three to six sentences.

---

## Tools and Technologies

List every tool, library, framework, API, and model your system uses. For each one, state what it does in your system, not just what it is.

| Tool or Technology | Version or Provider | What It Does in Your System |
|---|---|---|
|   |   |   |
|   |   |   |

---

## LLM Usage

**Model(s) used:**  
**Provider(s):**  
**Access method:** (API key / Hugging Face / local / other)  

List every place in your system where an LLM is called. For each call, describe what the LLM receives as input, what decision or output it produces, and how that output affects the next step.

| Step | LLM Input | LLM Output | Effect on System |
|---|---|---|---|
|   |   |   |   |
|   |   |   |   |

---

## Algorithms and Logic

Describe any non-trivial logic in your system. This includes retrieval strategies, scoring or ranking logic, classification rules, retry and fallback behavior, and any structured reasoning patterns you implemented.

If you used RAG, describe your chunking strategy, embedding model, and retrieval approach.  
If you used a graph-based agent framework, describe your node structure and transition conditions.  
If you implemented custom tool-calling logic, describe how the agent selects which tool to call and when.

---

## Deterministic vs Agentic Breakdown

This section is verified. Do not overstate the agentic percentage. Judges have access to your code and will check.

**Estimated breakdown:**

| Layer | Percentage | Description |
|---|---|---|
| Deterministic automation | % | What always happens the same way regardless of LLM output (triggers, API calls, data formatting, status updates) |
| LLM-driven and agentic | % | What the LLM decides, routes, interprets, or generates in a way that affects system behavior |

**Total must equal 100%.**

Describe in two to four sentences how the agentic layer affects system behavior. What would break or become worse if you replaced the LLM with a fixed script?

---

## Edge Cases Handled

List the edge cases from your problem statement that your system handles, and briefly describe the handling logic for each.

| Edge Case | How Your System Handles It |
|---|---|
|   |   |
|   |   |

If you did not implement handling for certain edge cases, list them here and explain why.

---

## Repository

**GitHub Repository Link:**  
**Branch submitted:** (main / submission / other)  
**Commit timestamp of final submission:** (paste the exact commit hash and timestamp in UTC)  

The repository must be public at the time of submission. Private repositories will not be reviewed.

The repository must contain a README that explains how to run the system locally, including environment setup, required API keys, and a sample input to test with. If the README does not exist or is insufficient, the submission will be penalised.

---

## Deployment

**Is your system deployed?** (Yes / No)  

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
```

---

## Deadlines

| Milestone | Time |
|---|---|
| Pull request must be opened | By 4:15 PM |
| All files must be in the PR | By 4:15 PM |

The pull request timestamp is final. Nothing pushed after 4:15 PM will be included in the evaluation.

---

## What Judges Will Check

Your summary document will be read before your demo. Judges will have your code open during your presentation. They will look for the following:

The LLM usage table will be verified against actual code. If you claim the LLM makes a decision at a certain step and the code shows a hardcoded conditional instead, that will be flagged.

The deterministic vs agentic breakdown will be spot-checked. Round numbers like "80% agentic" with no supporting explanation will be questioned.

The repository commit timestamp must fall within the event window (11:00 AM to 4:15 PM today). Commits timestamped before the event began are grounds for disqualification.

The README will be tested. If the setup instructions do not work, points will be deducted.

---

*Questions about the submission process must be directed to the event organisers before 3:30 PM.*
