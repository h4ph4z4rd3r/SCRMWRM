from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Contract(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="supplier.id")
    title: str
    status: str = Field(default="draft", description="draft, negotiation, active, expired")
    content_text: Optional[str] = Field(description="Full text of the contract for simple searching")
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
