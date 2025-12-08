from fastapi import APIRouter

router = APIRouter(prefix="/contract", tags=["contract"])

@router.get("/")
async def list_contracts():
    return {"message": "Contract module active"}
