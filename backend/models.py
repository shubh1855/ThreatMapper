from pydantic import BaseModel
from typing import List

class FlowRequest(BaseModel):
    flow: str

class Threat(BaseModel):
    component: str
    type: str
    description: str

class ThreatResponse(BaseModel):
    threats: List[Threat]
