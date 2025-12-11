# Roadmap: Release 2 (Simulation & Realism)

**Objective**: Upgrade the system from a logical skeleton to a fully functional simulator with real AI and believable data.

## Phase 1: Real Intelligence & World Building
**Goal**: Replace mock AI with OpenAI and populate the world with realistic contracts.
- [ ] **OpenAI Integration**:
    - Update `LLMClient` to use the official OpenAI SDK.
    - Add `OPENAI_API_KEY` to `Settings`.
    - Test `generate_json` and `generate_response` with GPT-4o.
- [ ] **Contract Generation**:
    - Create believable contract text/PDFs for:
        1.  **SaaS Subscription** (TechFlow Solutions)
        2.  **Cleaning Services** (CleanSwift Facilities)
        3.  **Data Processing** (DataVault Corp)
        4.  **ICT License** (GlobalSoft)
    - Seed the Database with these contracts and suppliers.

## Phase 2: The Opponent (Supplier Simulator)
**Goal**: Create an autonomous agent to act as the counter-party in negotiations.
- [ ] **Supplier Agent Logic**:
    - Create a separate Agent (or Node) `SupplierAgent` that acts on behalf of the external party.
    - Behavior driven by **Strategy Profiles** (YAML).
- [ ] **Strategy Configuration**:
    - Define profiles: `Aggressive`, `Collaborative`, `Stubborn`.
    - Yaml structure: `goals`, `walk_away_points`, `negotiation_style`.
- [ ] **Supplier Portal UI**:
    - A simple view to see the Supplier's perspective (or purely automated).

## Phase 3: The Battle Arena (Simulation)
**Goal**: Run Agent-vs-Agent simulations.
- [ ] **Auto-Negotiation Loop**:
    - Connect `NegotiatorAgent` output to `SupplierAgent` input.
    - Run episodes until "Signed" or "Walk-away".
- [ ] **Simulation Dashboard**:
    - View logs of Agent-vs-Agent interaction.
    - Metrics: "Turns to Agreement", "Satisfaction Score".
