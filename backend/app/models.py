from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

# Dynamic Vector Type based on available drivers/config
# Ideally we check settings, but simple try-import works for minimal dependencies
try:
    from pgvector.sqlalchemy import Vector
    vector_type = Vector(1536)
except ImportError:
    vector_type = JSON # Fallback for SQLite to avoid crashes on model definition

class ContractChunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    contract_id: UUID = Field(foreign_key="contract.id")
    chunk_index: int
    content: str
    # If using SQLite, this will just be a JSON field (no similarity search)
    embedding: List[float] = Field(sa_column=Column(vector_type))  
    
    contract: "Contract" = Relationship(back_populates="chunks")

class PolicyChunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    policy_id: UUID = Field(foreign_key="policy.id")
    chunk_index: int
    content: str
    embedding: List[float] = Field(sa_column=Column(vector_type))

    policy: "Policy" = Relationship(back_populates="chunks")

class SupplierRiskProfile(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    supplier_id: UUID = Field(foreign_key="supplier.id")
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Financials (D&B style)
    financial_stress_score: int = Field(default=0, description="1-100 (1 is bad)")
    credit_rating: str = Field(default="Unknown")
    
    # Reputation
    news_sentiment_score: float = Field(default=0.0, description="-1.0 to 1.0")
    adverse_media_count: int = Field(default=0)
    
    # Compliance
    sanctions_flag: bool = Field(default=False)
    sanctions_list_match: Optional[str] = None
    
    supplier: "Supplier" = Relationship(back_populates="risk_profiles")

class SupplierPerformance(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    supplier_id: UUID = Field(foreign_key="supplier.id")
    period_start: datetime
    period_end: datetime
    
    # KPI Scores (0-100)
    quality_score: float = Field(default=0.0, description="Defect rate, adherence to specs")
    delivery_score: float = Field(default=0.0, description="On-time delivery %")
    cost_score: float = Field(default=0.0, description="Price variance / Savings")
    
    overall_score: float = Field(default=0.0)
    
    supplier: "Supplier" = Relationship(back_populates="performance_reports")

class Supplier(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    domain: Optional[str] = None
    lei: Optional[str] = Field(default=None, description="Legal Entity Identifier")
    risk_score: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    contracts: List["Contract"] = Relationship(back_populates="supplier")
    risk_profiles: List["SupplierRiskProfile"] = Relationship(back_populates="supplier")
    performance_reports: List["SupplierPerformance"] = Relationship(back_populates="supplier")

class Policy(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    version: str
    text_content: str
    is_active: bool = True
    
    chunks: List["PolicyChunk"] = Relationship(back_populates="policy")

class Contract(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    supplier_id: Optional[UUID] = Field(default=None, foreign_key="supplier.id")
    title: str
    status: str = "draft"
    content_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    supplier: Optional[Supplier] = Relationship(back_populates="contracts")
    negotiations: List["Negotiation"] = Relationship(back_populates="contract")
    chunks: List["ContractChunk"] = Relationship(back_populates="contract")

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
