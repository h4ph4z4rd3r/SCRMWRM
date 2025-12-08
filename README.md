# SCRMWRM: The Agentic Contract War Room

**SCRMWRM** (Supplier CRM War Room) is an intelligent, agent-driven platform designed to empower contract managers during high-stakes supplier negotiations. It functions as a "War Room"—a central command center where policy, history, and strategy converge.

> **Mission**: To give contract managers a superhuman edge by synthesizing corporate policy ("The Lawyer"), supplier history ("The Analyst"), and strategic reasoning ("The Negotiator") into a real-time negotiation support system.

## Roadmap & Status

We are currently in **Phase 1: Foundation**. See our [Roadmap](./roadmap.md) for detailed plans.

- **Phase 1: Foundation** (Current) - establishing the Nexus Core API and database.
- **Phase 2: Data Ingestion** - PDF parsing, RAG, and Policy Engine.
- **Phase 3: Intelligence** - Supplier risk and performance scoring.
- **Phase 4: Agent Core** - LangGraph-driven negotiation strategy.
- **Phase 5: War Room UI** - The interactive frontend dashboard.

## Architecture: "The Negotiator's Hub"

The system is a **Modular Monolith** designed for extensibility:

*   **Nexus Core**: The central nervous system (FastAPI).
*   **Policy Engine ("The Lawyer")**: Checks compliance against corporate rules.
*   **Supplier Intelligence ("The Analyst")**: Provides context on vendor performance and risk.
*   **Contract Foundry ("The Scribe")**: Handles document parsing and generation.
*   **Agent Cortex ("The Negotiator")**: The AI brain synthesizing strategy.

## Technology Stack

*   **Backend**: Python 3.12+, FastAPI, LangGraph, Pydantic, SQLModel.
*   **Database**: PostgreSQL + pgvector (for RAG).
*   **Frontend**: React (Vite) + Tailwind/CSS Modules.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
