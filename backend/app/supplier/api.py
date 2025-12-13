from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import Supplier, SupplierPerformance
from pydantic import BaseModel

router = APIRouter(tags=["supplier"])

class PerformanceCreate(BaseModel):
    period_start: datetime
    period_end: datetime
    quality_score: float
    delivery_score: float
    cost_score: float

@router.get("/")
async def list_suppliers(session: Session = Depends(get_session)):
    # Simple list for debug
    from sqlmodel import select
    result = await session.exec(select(Supplier))
    return result.all()

@router.post("/{supplier_id}/performance", response_model=SupplierPerformance)
async def add_performance_report(
    supplier_id: UUID, 
    report: PerformanceCreate, 
    session: Session = Depends(get_session)
):
    """
    Ingest a new performance scorecard for a supplier.
    """
    supplier = await session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    # Calculate simple average for overall if not provided
    overall = (report.quality_score + report.delivery_score + report.cost_score) / 3.0
    
    perf_entry = SupplierPerformance(
        supplier_id=supplier_id,
        period_start=report.period_start,
        period_end=report.period_end,
        quality_score=report.quality_score,
        delivery_score=report.delivery_score,
        cost_score=report.cost_score,
        overall_score=overall
    )
    
    session.add(perf_entry)
    await session.commit()
    await session.refresh(perf_entry)
    
    return perf_entry
