import logging
import json
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models import Supplier, SupplierRiskProfile
from app.supplier.factory import get_supplier_data_provider
from app.llm import get_llm_client, LLMMessage

logger = logging.getLogger(__name__)

class SupplierIntelligenceService:
    """
    Orchestrates the gathering of external intelligence (Financial, News, Compliance)
    and uses the LLM (SCAnalyst) to synthesize a Risk Profile.
    """

    def __init__(self):
        self.data_provider = get_supplier_data_provider()
        self.llm = get_llm_client()

    async def _analyze_sentiment_and_risk(self, financials: dict, news: list, compliance: dict) -> dict:
        """
        Uses the LLM to analyze the raw data points and generate a derived risk assessment.
        """
        system_prompt = (
            "You are the SCAnalyst, an expert Supplier Risk Manager.\n"
            "Analyze the provided raw data (Financials, News, Sanctions) and output a JSON assessment.\n"
            "Output Schema:\n"
            "{\n"
            "  \"news_sentiment_score\": float, // -1.0 (Critical Negative) to 1.0 (Positive)\n"
            "  \"risk_summary\": string, // A brief 2-sentence executive summary of the risk.\n"
            "  \"recommended_action\": string // 'HOLD', 'MONITOR', 'PROCEED'\n"
            "}"
        )

        user_content = (
            f"--- FINANCIALS ---\n{json.dumps(financials)}\n"
            f"--- COMPLIANCE ---\n{json.dumps(compliance)}\n"
            f"--- NEWS HEADLINES ---\n{json.dumps(news)}"
        )

        messages = [LLMMessage(role="user", content=user_content)]

        schema = {
            "type": "object",
            "properties": {
                "news_sentiment_score": {"type": "number"},
                "risk_summary": {"type": "string"},
                "recommended_action": {"type": "string", "enum": ["HOLD", "MONITOR", "PROCEED"]}
            },
            "required": ["news_sentiment_score", "risk_summary", "recommended_action"]
        }

        try:
            return await self.llm.generate_json(messages, schema, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"LLM Risk Analysis failed: {e}")
            return {
                "news_sentiment_score": 0.0,
                "risk_summary": "Automated analysis failed.",
                "recommended_action": "MONITOR"
            }

    async def update_supplier_risk_profile(self, session: Session, supplier_id: UUID) -> SupplierRiskProfile:
        """
        Full workflow: Fetch Data -> Analyze(LLM) -> Save DB.
        """
        # 1. Get Supplier
        supplier = await session.get(Supplier, supplier_id)
        if not supplier:
            raise ValueError(f"Supplier {supplier_id} not found")

        # 2. Fetch External Data (Parallelizable in future)
        # Assuming we store DUNS in 'lei' field or similar for now, or use name.
        # Fallback to a mock DUNS or use internal ID if specific fields missing.
        duns = supplier.lei or "000000000" 
        
        financials = await self.data_provider.get_financial_health(duns)
        news = await self.data_provider.get_market_news(supplier.name)
        # Determine country code context. Defaulting to 'US' or extracting if we had address fields.
        compliance = await self.data_provider.check_compliance(supplier.name, "US")

        # 3. LLM Analysis
        analysis = await self._analyze_sentiment_and_risk(financials, news, compliance)

        # 4. Create/Update Risk Profile
        # We create a new snapshot history rather than overwriting? 
        # The model usually implies a history if we just append to list.
        # But here we are just adding a new row.
        
        risk_profile = SupplierRiskProfile(
            supplier_id=supplier.id,
            retrieved_at=datetime.now(timezone.utc),
            
            # Map Data Provider fields
            financial_stress_score=financials.get("financial_stress_score", 0),
            credit_rating=financials.get("credit_rating", "N/A"),
            
            # Map Compliance
            sanctions_flag=compliance.get("sanctions_flag", False),
            sanctions_list_match=compliance.get("list_match"),
            
            # Map LLM Analysis
            news_sentiment_score=analysis.get("news_sentiment_score", 0.0),
            adverse_media_count=len([n for n in news if n.get('sentiment') == 'negative'])
        )

        session.add(risk_profile)
        
        # 5. Update main Supplier score for quick access?
        # A simple heuristic: 
        # Risk Score (0-100, where 100 is high risk? or low risk?).
        # Let's align with: Risk Score = 0 (Safe) to 100 (Critical).
        # Financial Stress (1-100, 100 is good). So (100 - FinScore).
        # Sentiment (-1 to 1). -1 is bad.
        
        # Simple weighted formula
        fin_risk = 100 - financials.get("financial_stress_score", 50)
        sentiment_risk = (1.0 - analysis.get("news_sentiment_score", 0)) * 50 # Maps -1->100, 1->0
        
        combined_risk = (fin_risk * 0.6) + (sentiment_risk * 0.4)
        if compliance.get("sanctions_flag"):
            combined_risk = 100.0
            
        supplier.risk_score = min(max(combined_risk, 0.0), 100.0)
        session.add(supplier)
        
        await session.commit()
        await session.refresh(risk_profile)
        
        return risk_profile
