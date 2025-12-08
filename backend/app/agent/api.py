from fastapi import APIRouter

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/negotiate")
async def start_negotiation():
    return {"message": "Negotiation started", "status": "analyzing"}
