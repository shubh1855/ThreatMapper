from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import (
    FlowRequest,
    ThreatResponse,
    Threat,
    DreadRequest,
    DreadResponse
)

from stride_agent import analyze_system_flow

app = FastAPI()

# CORS (allow frontend to access backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backend running"}

@app.post("/analyze", response_model=ThreatResponse)
def analyze_flow(flow_request: FlowRequest):
    """
    Accepts a system flow and returns STRIDE threats (no DREAD scoring yet).
    """
    threats = analyze_system_flow(flow_request.flow)
    return {"threats": threats}

@app.post("/dread", response_model=DreadResponse)
def calculate_overall_dread(dread: DreadRequest):
    """
    Accepts 5 DREAD metric values for the system overall,
    calculates the average and returns a single score.
    """
    values = [
        dread.damage,
        dread.reproducibility,
        dread.exploitability,
        dread.affected_users,
        dread.discoverability
    ]
    score = round(sum(values) / 5.0, 2)
    return {"score": score}
