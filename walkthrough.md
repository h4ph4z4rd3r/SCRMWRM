# The War Room: Quick Start Guide

This guide explains how to launch the **Agentic Contract Negotiator** and the **War Room Dashboard**.

## 1. Start the Backend (The Brain)

The backend runs the LangGraph agent and the API.

```bash
cd backend
# Ensure virtualenv is active
source ../.venv/bin/activate
# Run FastAPI (Defaults to SQLite for local dev)
uvicorn app.main:app --reload --port 8000
```

*   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Agent Endpoint**: `POST /api/v1/agent/negotiate`

## 2. Start the Frontend (The Review)

The frontend provides the visual "War Room" interface.

```bash
cd frontend
# Install dependencies (if not done)
npm install
# Run Dev Server
npm run dev
```

*   **Dashboard**: [http://localhost:5173/](http://localhost:5173/)

## 3. Human-in-the-Loop Workflow

1.  Open the **Dashboard**.
2.  Click on any active Negotiation (or create one via the Backend API for now).
3.  Simulate a message exchange.
4.  If the Agent enters `Action Required` mode (based on `AGENCY_LEVEL` or high risk):
    *   The thread will pause.
    *   A "Proposed Strategy" box will appear in the chat.
    *   Click **Approve** to resume the Agent.
5.  The Agent will draft the response and the chat will update.
