# Agentic Contract Change Negotiator

A modular, AI-powered system to assist contract managers in negotiating supplier agreements.

## Architecture: "The Negotiator's Hub"

This project follows a **Modular Monolith** architecture, designed to be API-First and easily transitionable to microservices.

### Modules

*   **Nexus Core**: The central API gateway, orchestration layer, and auth handler.
*   **Policy Engine**: The "Lawyer". Ingests corporate policy and uses AI to check for compliance.
*   **Supplier Intelligence**: The "Analyst". Manages supplier risk, performance, and portfolio data.
*   **Contract Foundry**: The "Scribe". Parses, manages, and drafts contract documents.
*   **Agent Cortex**: The "Negotiator". synthesizing inputs to formulate strategy and arguments.

## Technology Stack

*   **Backend**: Python 3.12+, FastAPI, LangGraph, Pydantic, SQLModel.
*   **Database**: PostgreSQL + pgvector.
*   **Frontend**: React (Vite), plain CSS / CSS Modules.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
