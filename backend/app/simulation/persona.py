from typing import List, Optional
from pydantic import BaseModel
import yaml

class SupplierGoal(BaseModel):
    description: str
    threshold: float = 0.0 # e.g., min price, max liability cap

class SupplierPersona(BaseModel):
    id: str
    name: str
    style: str # "Aggressive", "Collaborative", "Passive"
    goals: List[str]
    constraints: List[str]
    negotiation_tone: str = "professional"
    
    @classmethod
    def load_from_yaml(cls, path: str) -> "SupplierPersona":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)
