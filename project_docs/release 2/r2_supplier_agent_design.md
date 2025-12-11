# Release 2: Supplier Simulation Agent Design

## 1. Overview
The **Supplier Agent** is a standalone autonomous entity designed to test the `NegotiatorAgent`. It simulates a counter-party with specific goals, personality, and constraints.

## 2. Architecture

### 2.1 The "Persona" (YAML)
Each supplier is defined by a YAML profile in `backend/data/suppliers/`.

```yaml
id: "techflow-saas"
name: "TechFlow Solutions"
style: "Aggressive" # Aggressive, Collaborative, Passive
goals:
  - "Maximize revenue (no discounts > 5%)"
  - "Keep 3-year term"
constraints:
  - "Cannot accept unlimited liability"
  - "Must have Net 30 or less"
initial_redline: |
  (The starting text of the contract variations)
```

### 2.2 The Logic (State Machine)
The Supplier Agent is simpler than the Negotiator. It loops:
1.  **Read Proposal**: Evaluate incoming redline against `goals` + `constraints`.
2.  **Evaluate Satisfaction**: Score the current deal (0-100).
3.  **Decide**:
    *   `ACCEPT`: If Score > Threshold.
    *   `REJECT`: If Critical Constraint violated (and stuck).
    *   `COUNTER`: Modify text to move closer to goals.
4.  **Generative Response**: Use LLM to write the email/message response in the "Voice" of the persona (`style`).

## 3. Implementation Steps

1.  **Model**: Add `SupplierPersona` Pydantic model.
2.  **Loader**: Utilities to load YAMLs.
3.  **Sim Loop**: A script or API endpoint `POST /simulate/turn` that takes the current state and returns the Supplier's move.
4.  **UI**: A simple "Battle Console" showing the two agents talking to each other.

## 4. Integration
*   The `Negotiation` model in the DB needs a `simulation_id` to track these auto-battles.
*   We will use the same `OpenAIClient` for the Supplier Agent but with a different System Prompt.
