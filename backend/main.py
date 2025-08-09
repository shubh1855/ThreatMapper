from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import FlowRequest, ThreatResponse
from stride_agent import analyze_system_flow

app = FastAPI()

# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=ThreatResponse)
def analyze_flow(flow_request: FlowRequest):
    threats = analyze_system_flow(flow_request.flow)
    return {"threats": threats}

@app.get("/")
def home():
    return {"status": "Backend running"}
