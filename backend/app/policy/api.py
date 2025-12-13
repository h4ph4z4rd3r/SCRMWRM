from fastapi import APIRouter
from app.models import Policy

router = APIRouter(tags=["policy"])

@router.get("/")
async def list_policies():
    return {"message": "Policy module active"}

@router.post("/check")
async def check_compliance(clause: str):
    # Placeholder for Agent/RAG logic
    return {"compliant": True, "analysis": "Placeholder analysis"}
