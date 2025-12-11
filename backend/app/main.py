from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nexus_core")

# Define lifespan (startup/shutdown) events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB, models, etc.
    logger.info("Nexus Core: System Initializing...")
    from app.database import init_db
    await init_db()
    yield
    # Shutdown: Clean up connections
    logger.info("Nexus Core: System Shutting Down...")

app = FastAPI(
    title="Agentic Contract Negotiator",
    description="API for the AI-driven negotiation support system.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

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
from app.simulation import api as simulation

app.include_router(policy.router, prefix="/api/v1/policy", tags=["policy"])
app.include_router(supplier.router, prefix="/api/v1/supplier", tags=["supplier"])
app.include_router(contract.router, prefix="/api/v1/contract", tags=["contract"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["simulation"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
