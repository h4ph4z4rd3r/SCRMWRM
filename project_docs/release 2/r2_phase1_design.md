# Release 2 - Phase 1 Design: Real Intelligence

## 1. OpenAI Integration
We will replace the mock LLM client with the `openai` Python SDK.

### 1.1 Configuration
*   **Env Var**: `OPENAI_API_KEY`
*   **Model**: `gpt-4o` (High intelligence for negotiation), `gpt-3.5-turbo` (Fast summary/classification).

### 1.2 Implementation (`app/llm/openai_client.py`)
*   Implement `AbstractLLMClient`.
*   `generate_response`: Uses `client.chat.completions.create`.
*   `generate_json`: Uses `response_format={"type": "json_object"}`.

## 2. World Building: Seed Data

We will create a `populate_db.py` script to inject the following scenarios:

### 2.1 Scenario A: The SaaS Lock-in
*   **Supplier**: *TechFlow Solutions* (Risk: Low).
*   **Contract**: "Enterprise SaaS Subscription Agreement".
*   **Issue**: **auto-renewal** for 3 years (Policy Violation: Max 1 year).
*   **Supplier Context**: Confident market leader.

### 2.2 Scenario B: The GDPR Nightmare
*   **Supplier**: *DataVault Corp* (Risk: High - Data Breach Risk).
*   **Contract**: "Data Processing Addendum".
*   **Issue**: **Liability Cap** is $5k (Policy Requirement: Unlimited for Data Breaches).
*   **Supplier Context**: Nervous about liability.

### 2.3 Scenario C: The Facilities Fix
*   **Supplier**: *CleanSwift Facilities* (Risk: Medium).
*   **Contract**: "Services Agreement".
*   **Issue**: **Payment Terms** Net 7 (Policy Requirement: Net 45).
*   **Supplier Context**: Small business, cash flow sensitive.

### 2.4 Scenario D: The Licensing Gaps
*   **Supplier**: *GlobalSoft* (Risk: Low).
*   **Contract**: "ICT License Framework".
*   **Issue**: **Audit Rights** missing (Policy Requirement: Annual Audit Right).
*   **Supplier Context**: Standard behemoth.

## 3. Execution Plan
1.  Add `openai` to `requirements.txt`.
2.  Implement `OpenAIClient`.
3.  Bind `LLM_PROVIDER="openai"` in settings.
4.  Create `scripts/seed_data.py` with the scenarios above.
