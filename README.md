# SCRMWRM: The Agentic Contract War Room

**SCRMWRM** (Supplier CRM War Room) is an intelligent, agent-driven platform designed to empower contract managers during high-stakes supplier negotiations. It functions as a "War Room"—a central command center where policy, history, and strategy converge.

> **Mission**: To give contract managers a superhuman edge by synthesizing corporate policy ("The Lawyer"), supplier history ("The Analyst"), and strategic reasoning ("The Negotiator") into a real-time negotiation support system.

## Roadmap & Status

We are currently entering **Phase 3: Intelligence**. See our [Roadmap](./roadmap.md) for detailed plans.

- **Phase 1: Foundation** (Completed) - Nexus Core API, Database, Schemas.
- **Phase 2: Data Ingestion & Core Intelligence** (Completed) - Hybrid LLM (Bedrock/Mistral), PDF Parsing, Policy RAG, and Security.
- **Phase 3: Intelligence** (Completed) - Supplier risk profiling, KPIs, and External Data Adapters.
- **Phase 4: Agent Core** (Next) - LangGraph-driven negotiation strategy.
- **Phase 5: War Room UI** - The interactive frontend dashboard.

## Architecture:

The system is a **Modular Monolith** designed for extensibility:

*   **Nexus Core**: The central nervous system (FastAPI).
*   **Policy Engine ("The Lawyer")**: Checks compliance against corporate rules.
*   **Supplier Intelligence ("The Analyst")**: Provides context on vendor performance and risk.
*   **Contract Foundry ("The Scribe")**: Handles document parsing and generation.
*   **Agent Cortex ("The Negotiator")**: The AI brain synthesizing strategy.

## Workflow: The Agentic Orchestration

In a typical negotiation scenario (e.g., receiving a contract redline), the agents collaborate as follows:

1.  **Ingestion ("The Scribe")**:
    *   **Action**: `SCScribe` parses the uploaded PDF/Docx using the `PDFParser`.
    *   **Outcome**: The text is cleaned, chunked, and stored in the vector database (`pgvector`) for semantic retrieval.

2.  **Compliance Check ("The Lawyer")**:
    *   **Action**: `SCLawyer` retrieves relevant corporate policies (`RAGService`) matching the contract clauses.
    *   **Outcome**: The `PolicyEngine` (Sandboxed LLM) evaluates the text and flags violations (e.g., *"Supplier requested Net 15 payment terms, but Corporate Policy #88 requires Net 60"*).

3.  **Risk Assessment ("The Analyst")**:
    *   **Action**: `SCAnalyst` queries the `SupplierIntelligenceService`.
    *   **Outcome**: It combines Real-time Financials (D&B), News Sentiment (NewsAPI), and internal Performance Scores (`SupplierPerformance`) to calculate a leverage score.
        *   *Insight Example*: "Supplier is financially stressed (Score: 30/100) and has quality issues, giving us high negotiation leverage."

4.  **Strategy Synthesis ("The Negotiator")**:
    *   **Action**: The Orchestrator combines the Lawyer's *Constraints* and the Analyst's *Insights*.
    *   **Outcome**: It formulates a strategy: *"Reject Net 15. Counter with Net 45. Use their poor delivery score as leverage to maintain the penalty clause."*

5.  **Drafting ("The Scribe")**:
    *   **Action**: `SCScribe` generates the precise legal text for the counter-proposal based on the Negotiator's strategy.
    *   **Outcome**: A ready-to-send contract version.

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
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
