from fastapi import APIRouter

router = APIRouter(tags=["contract"])

@router.get("/")
async def list_contracts():
    return {"message": "Contract module active"}
