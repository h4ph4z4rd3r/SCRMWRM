from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.simulation.agent import SupplierAgent

router = APIRouter()

class SimulationTurnRequest(BaseModel):
    persona_id: str
    conversation_history: List[Dict[str, str]] # list of {sender: "", content: ""}
    latest_proposal: str

class SimulationTurnResponse(BaseModel):
    response: str

@router.post("/turn", response_model=SimulationTurnResponse)
async def run_simulation_turn(request: SimulationTurnRequest):
    try:
        agent = SupplierAgent(request.persona_id)
        response = await agent.generate_reply(request.conversation_history, request.latest_proposal)
        return SimulationTurnResponse(response=response)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Persona {request.persona_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
