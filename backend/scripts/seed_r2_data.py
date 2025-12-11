import asyncio
import os
import sys

# Add parent dir to path so we can import app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import get_session, init_db
from app.models import Supplier, Contract, Policy, SupplierRiskProfile
from app.llm import get_llm_client, LLMMessage
from app.agent.state import NegotiationState

scenarios = [
    {
        "name": "Scenario A: SaaS Auto-Renewal",
        "supplier": "TechFlow Solutions",
        "risk_score": 15.0,
        "contract_title": "Enterprise Subscription Agreement",
        "policy_violation": "Auto-renewal for 3 years (Max 1 year)",
        "prompt": "Write a 2-page Enterprise SaaS Agreement. Include a clause stating 'This agreement shall automatically renew for successive terms of three (3) years unless terminated with 6 months notice'."
    },
    {
        "name": "Scenario B: Data Breach Liability",
        "supplier": "DataVault Corp",
        "risk_score": 85.0,
        "contract_title": "Data Processing Addendum",
        "policy_violation": "Liability Cap $5k (Required: Unlimited for Breach)",
        "prompt": "Write a Data Processing Addendum. Include a clause: 'Provider's total liability for any data breach or loss shall be strictly limited to $5,000 USD'."
    },
    {
        "name": "Scenario C: Payment Terms",
        "supplier": "CleanSwift Facilities",
        "risk_score": 45.0,
        "contract_title": "Cleaning Services Master Agreement",
        "policy_violation": "Payment Net 7 (Required: Net 45)",
        "prompt": "Write a Facilities Service Agreement. Include: 'All invoices are due and payable within seven (7) days of receipt (Net 7).'"
    },
    {
        "name": "Scenario D: Audit Rights",
        "supplier": "GlobalSoft Licenses",
        "risk_score": 10.0,
        "contract_title": "Software License Framework",
        "policy_violation": "No Audit Rights (Required: Annual)",
        "prompt": "Write a specialized Software License Agreement. Explicitly state: 'Licensor shall have no right to audit Licensee's systems or records regarding usage of the Software.'"
    }
]

async def seed_data():
    print("Initializing DB...")
    await init_db()
    
    llm = get_llm_client()
    
    async for session in get_session():
        for scen in scenarios:
            print(f"Generating content for: {scen['supplier']}...")
            
            # 1. Generate Contract Text
            messages = [
                LLMMessage(role="system", content="You are a lawyer writing specific contract clauses."),
                LLMMessage(role="user", content=scen['prompt'])
            ]
            
            try:
                contract_text = await llm.generate_response(messages)
            except Exception as e:
                print(f"Error generating text (LLM might not be configured): {e}")
                contract_text = f"Mock Contract Content for {scen['contract_title']}\n\nClause: {scen['policy_violation']}"

            # 2. Create Supplier
            supplier = Supplier(
                name=scen['supplier'],
                risk_score=scen['risk_score']
            )
            session.add(supplier)
            await session.commit()
            await session.refresh(supplier)
            
            # 3. Create Contract
            contract = Contract(
                supplier_id=supplier.id,
                title=scen['contract_title'],
                content_text=contract_text,
                status="draft"
            )
            session.add(contract)
            await session.commit()
            
            # 4. Create Negotiation (Thread)
            from app.models import Negotiation
            negotiation = Negotiation(
                contract_id=contract.id,
                status="active",
                strategy="Initial Review",
                goals="Ensure compliance with company policy.",
                min_limits="Standard terms"
            )
            session.add(negotiation)
            await session.commit()
            
            print(f"Created {scen['supplier']} -> Contract {contract.id} -> Negotiation {negotiation.id}")

if __name__ == "__main__":
    asyncio.run(seed_data())
