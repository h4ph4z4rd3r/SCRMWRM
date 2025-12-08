from fastapi import APIRouter
from app.policy.models import PolicyDocument

router = APIRouter(prefix="/policy", tags=["policy"])

@router.get("/")
async def list_policies():
    return {"message": "Policy module active"}

@router.post("/check")
async def check_compliance(clause: str):
    # Placeholder for Agent/RAG logic
    return {"compliant": True, "analysis": "Placeholder analysis"}
