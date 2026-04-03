# Agentic AI System for Scrollhouse

## 1. Introduction
This project presents an Agentic AI system designed to automate two key workflows:
- Client Onboarding (PS-01)  
- Content Brief Processing (PS-02)  

The system performs end-to-end automation, decision-making, and logging.

---

## 2. Objective
- Reduce manual work  
- Improve accuracy  
- Automate repetitive tasks  
- Provide centralized workflow management  

---

## 3. System Overview
The system uses AI agents to:
- Validate inputs  
- Make decisions  
- Execute workflows  
- Handle errors  
- Log all activities  

---

## 4. Client Onboarding Workflow (PS-01)

### Steps:
1. Validate required fields  
2. Check duplicate brand in Airtable  
3. Send welcome email  
4. Create Google Drive folder  
5. Generate Notion client hub  
6. Store client data in Airtable  
7. Notify account manager  
8. Log all actions  

### Output:
- Email sent  
- Drive structure created  
- Notion hub ready  
- Airtable updated  

---

## 5. Content Brief Processing Workflow (PS-02)

### Steps:
1. Detect new brief  
2. Parse input data  
3. Retrieve brand context  
4. Rewrite into structured format  
5. Create Notion brief page  
6. Notify scriptwriter  
7. Update Airtable  
8. Log workflow  

### Output:
- Structured brief  
- Notion page created  
- Scriptwriter notified  
- Airtable updated  

---

## 6. Error Handling
- Missing inputs → workflow paused  
- Duplicate brand → confirmation required  
- API failures → retry mechanism  
- Incomplete brief → flagged for review  
- Resource unavailable → auto reassignment  

---

## 7. Technology Stack
- LangChain & LangGraph  
- Antigravity  
- n8n  
- FAISS / LangDB  
- Airtable  
- Notion  
- Google Drive  
- Slack  
- LangSmith  

---

## 8. System Architecture
The system follows a modular architecture:
- Input Layer  
- AI Decision Layer  
- API Execution Layer  
- Storage Layer  
- Logging Layer  

---

## 9. Deployment
- Hosted using Vercel  
- Serverless API endpoints  
- Environment variables for security  

---

## 10. Benefits
- Faster onboarding  
- Efficient content processing  
- Reduced manual errors  
- Scalable system  
- Full audit trail  

---

## 11. Conclusion
This Agentic AI system provides a complete automation solution for Scrollhouse, ensuring efficiency, accuracy, and scalability.