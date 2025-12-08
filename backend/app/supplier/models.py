from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    contact_email: Optional[str] = None
    risk_score: float = Field(default=0.0, description="0.0 to 1.0 representing calculated risk")
    performance_rating: float = Field(default=0.0, description="0.0 to 5.0 performance score")
    status: str = Field(default="active", description="active, suspended, under_review")
    created_at: datetime = Field(default_factory=datetime.utcnow)
