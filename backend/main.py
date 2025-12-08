from fastapi import FastAPI
from contextlib import asynccontextmanager

# Define lifespan (startup/shutdown) events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB, models, etc.
    print("Nexus Core: System Initializing...")
    yield
    # Shutdown: Clean up connections
    print("Nexus Core: System Shutting Down...")

app = FastAPI(
    title="Agentic Contract Change Negotiator",
    description="API for the AI-driven negotiation support system.",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "system": "Nexus Core",
        "status": "online",
        "message": "Welcome to the Agentic Contract Negotiator API"
    }

from app.policy import api as policy
from app.supplier import api as supplier
from app.contract import api as contract
from app.agent import api as agent

app.include_router(policy.router)
app.include_router(supplier.router)
app.include_router(contract.router)
app.include_router(agent.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
