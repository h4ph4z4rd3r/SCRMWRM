from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    contract_context: str
    policy_context: str
    supplier_risk: float

# Placeholder graph definition
# from langgraph.graph import StateGraph, END
# graph = StateGraph(AgentState)
# ... define nodes ...
