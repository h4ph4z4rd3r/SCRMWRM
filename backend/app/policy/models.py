from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class PolicyDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content_hash: str # To avoid duplicates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships could go here
    # chunks: List["PolicyChunk"] = Relationship(back_populates="document")

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column

class PolicyChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="policydocument.id")
    content: str
    embedding: List[float] = Field(sa_column=Column(Vector(1536))) # OpenAI dimension default

    # document: Optional[PolicyDocument] = Relationship(back_populates="chunks")
