from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Construct the Async Database URL
# Note: In a real scenario, this would come from settings. 
# For now, we fallback to a default if not set, or raise error.
# Construct the Async Database URL
# Use SQLite as default fallback if no ENV is set, to ensure it works without Docker
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI or "sqlite+aiosqlite:///./negotiator.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        # Import models so SQLModel knows about them
        from app import models
        from sqlalchemy import text
        
        # Only try to create extension for Postgres
        if "postgresql" in DATABASE_URL:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
        await conn.run_sync(SQLModel.metadata.create_all)
