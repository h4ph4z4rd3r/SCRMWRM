# SCRMWRM Roadmap

This document correlates the project vision with validatable implementation phases. The goal is to move from a "System of Record" to a "System of Intelligence" to a "System of Agency".

## Phase 1: Foundation (Completed) ✅
**Goal:** Establish the Nexus Core API, database schema, and project structure.
- [x] **Project Setup**: Repository structure, `poetry`/`venv`, and environment configuration.
- [x] **Database Design**: `SQLModel` schemas for Suppliers, Contracts, Policies, and Negotiations.
- [x] **API Core**: FastAPI application skeleton with modular routing (`app/policy`, `app/supplier`, etc.).
- [x] **Security**: Basic environment variable management (`.env`) for secrets.

## Phase 2: The Cortex & "The Eyes" (Completed) ✅
**Goal:** Enable the system to "read" documents, "think" using LLMs, and "judge" compliance.
- [x] **Hybrid LLM Service**:
    - Abstraction layer (`AbstractLLMClient`) supporting hot-swapping providers.
    - **Primary**: AWS Bedrock (Claude 3.5 Sonnet) for high-reasoning tasks in EU (Frankfurt).
    - **Sovereign Fallback**: Mistral AI (Mistral Large) for strict data residency.
- [x] **Contract Foundry ("The Scribe")**:
    - Secure PDF Parser (`PDFParser`) with file size and type validation.
    - Chunking logic for breaking down legal texts.
- [x] **RAG Engines**:
    - `pgvector` integration for semantic search.
    - `RAGService` for ingesting and searching both **Contracts** and **Corporates Policies**.
- [x] **Policy Engine ("The Lawyer")**:
    - `PolicyEvaluator` using LLMs to audit contract text against defined policies.
    - Anti-Injection defenses ("Sandboxed" prompts).
- [x] **Testing**: `pytest` framework with async support and security unit tests.

## Phase 3: Supplier Intelligence ("The Analyst") (Completed) ✅
**Goal:** Integrate data sources to assess supplier risk and performance.
- [x] **External Data Integration**:
    - `SupplierRiskProfile` model in SQLModel.
    - Adapter Pattern (`ExternalDataProvider`) implemented.
    - `MockDataProvider` created for simluating financial/compliance risks.
    - `SupplierIntelligenceService` implemented to aggregate data and use LLM for synthesis.
- [x] **Performance Scorecards**: API to ingest and calculate supplier KPI scores.
- [x] **Risk Scoring Engine**: (Base v1) Logic to combine Financial, Geopolitical, and Performance data into a single "Risk Score".

## Phase 4: Agentic Orchestration ("The Negotiator") (Completed) ✅
**Goal:** Synthesize inputs from Lawyer, Scribe, and Analyst into actionable strategy.
- [x] **LangGraph Setup**: Define the state graph (`NegotiationState`) and install dependencies.
- [x] **Agent Workflow**:
    - `PolicyNode` (Lawyer)
    - `RiskNode` (Analyst)
    - `StrategyNode` (Negotiator)
    - `DraftingNode` (Scribe)
    - Wiring the Graph topology.
- [x] **Human-in-the-Loop**:
    - Variable Agency Levels (Strict, Medium, Autonomous).
    - `GatekeeperNode` for Graph interruptions.
    - API endpoints to `POST /resume` triggered workflows.

## Phase 5: The War Room (Frontend) (Completed) ✅
**Goal:** A "Minority Report" style dashboard for the Contract Manager.
- [x] **Scaffold**: Initialize React + Vite + Tailwind project.
- [x] **Dashboard View**: Kanban/List of active negotiations with status indicators.
- [x] **Negotiation View**:
    - Left Panel: Supplier Logic (Risk/Policy).
    - Center Panel: Chat Interface (Input & Graph States).
    - Right Panel: Document Diff Viewer.
- [x] **Integration**: Connect Frontend to `POST /agent/negotiate` and `POST /agent/resume`.
