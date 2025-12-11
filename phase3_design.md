# Phase 3: Supplier Intelligence - External Data Integration Strategy

To empower the **SCAnalyst** agent, we need to inject real-world context into the system. This allows the agent to say *"We shouldn't accept these payment terms because this supplier has a high bankruptcy risk"* rather than just tracking the contract status.

## 1. Recommended Data Sources

### A. Financial Health: Dun & Bradstreet (D&B)
*   **Why**: The global standard for commercial data. Provides "Failure Score", "Delinquency Score", and corporate hierarchy.
*   **Role**: Critical for assessing if a supplier will exist in 12 months.
*   **Integration**:
    *   **Method**: D&B Direct+ API.
    *   **Strategy**: Since this is an expensive enterprise API, we will implement a **Mock Adapter** by default that returns realistic, randomized data for development. We will define the strict Interface so the real API can be swapped in later (Dependency Injection).

### B. Reputation & ESG: NewsAPI.org
*   **Why**: Real-time access to global news. Allows the agent to catch recent scandals, lawsuits, or strikes that haven't hit the financial reports yet.
*   **Role**: Sentiment analysis. The Agents will read the headlines/summaries and adjust the "Leverage Score".
*   **Integration**:
    *   **Method**: HTTP REST API.
    *   **Strategy**: Free tier is available for developer use. we will implement a real client that takes an API key, with a fallback to mock data if no key is present.

### C. Compliance & Sanctions: OpenSanctions
*   **Why**: Aggregates sanctions lists (EU, OFAC, UN) and PEPs (Politically Exposed Persons). Crucial for EU compliance.
*   **Role**: "The Lawyer" agent uses this to veto suppliers in restricted regions.
*   **Integration**:
    *   **Method**: Reconciliation API (or self-hosted yml database).
    *   **Strategy**: We will use a lightweight "Sanctions Check" mock that flags specific test names (e.g., "North Korea Imports Ltd") for the demo.

## 2. Architecture: "The Intelligence Nexus"

We will build a modular **Supplier Intelligence Service** in `app/supplier/intelligence.py`.

### 2.1 The Data Models (`app/models.py`)
We need to expand the `Supplier` model to store the "Snapshot" of this external data.

```python
class SupplierRiskProfile(SQLModel, table=True):
    id: UUID
    supplier_id: UUID
    retrieved_at: datetime
    
    # Financials (D&B style)
    financial_stress_score: int # 1-100 (1 is bad)
    credit_rating: str          # e.g., "5A1"
    
    # Reputation
    news_sentiment_score: float # -1.0 to 1.0 (derived from LLM analysis of news)
    adverse_media_count: int
    
    # Compliance
    sanctions_flag: bool
    sanctions_list_match: Optional[str]
```

### 2.2 The Adapter Pattern
We will define an abstract base class `ExternalDataProvider` to ensure we aren't locked into specific vendors.

```python
class ExternalDataProvider(ABC):
    @abstractmethod
    async def get_financial_health(self, duns_number: str) -> Dict: ...
    
    @abstractmethod
    async def get_market_news(self, company_name: str) -> List[str]: ...
```

## 3. Implementation Plan

1.  **Define Interfaces**: Create `app/supplier/adapters/base.py`.
2.  **Implement Mock Provider**: Create `app/supplier/adapters/mock.py` to generate realistic "Risk Scenarios" (e.g., "High Risk Supplier", "Stable Supplier") for testing.
3.  **Implement News Integration**: Create `app/supplier/adapters/news_api.py`.
    *   *Action Required*: You (User) will need a free API key from newsapi.org eventually.
4.  **Update Database**: Add `SupplierRiskProfile` table.
5.  **Intelligence Service**: Create the service that orchestrates fetching this data and—critically—**uses the LLM to summarize it** into a single "Risk Score" for the Negotiator.

## 4. Why this approach?
*   **Cost Effective**: No immediate need for expensive D&B contracts.
*   **Testable**: We can force specific risk scenarios (e.g., "Supplier declares bankruptcy") to verify Agent behavior.
*   **Extensible**: Swapping D&B for Experian or Creditsafe is just a new Adapter class.
