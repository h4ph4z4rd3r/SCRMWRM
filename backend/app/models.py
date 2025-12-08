from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class Supplier(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    domain: Optional[str] = None
    lei: Optional[str] = Field(default=None, description="Legal Entity Identifier")
    risk_score: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    contracts: List["Contract"] = Relationship(back_populates="supplier")

class Policy(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    version: str
    text_content: str
    is_active: bool = True

class Contract(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    supplier_id: Optional[UUID] = Field(default=None, foreign_key="supplier.id")
    title: str
    status: str = "draft"
    content_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    supplier: Optional[Supplier] = Relationship(back_populates="contracts")
    negotiations: List["Negotiation"] = Relationship(back_populates="contract")

class Negotiation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    contract_id: UUID = Field(foreign_key="contract.id")
    status: str = Field(default="active", description="active, completed, stalled")
    strategy: Optional[str] = Field(default=None, description="AI generated strategy")
    goals: Optional[str] = Field(default=None, description="Negotiation targets")
    min_limits: Optional[str] = Field(default=None, description="Walk-away points")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    contract: Contract = Relationship(back_populates="negotiations")
    messages: List["NegotiationMessage"] = Relationship(back_populates="negotiation")

class NegotiationMessage(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    negotiation_id: UUID = Field(foreign_key="negotiation.id")
    content: str
    type: str = Field(description="proposal or response")
    sender: str = Field(description="company or supplier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    negotiation: Negotiation = Relationship(back_populates="messages")
