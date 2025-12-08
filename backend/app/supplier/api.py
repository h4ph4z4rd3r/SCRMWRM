from fastapi import APIRouter

router = APIRouter(prefix="/supplier", tags=["supplier"])

@router.get("/")
async def list_suppliers():
    return {"message": "Supplier module active"}
