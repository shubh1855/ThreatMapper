import os
import uuid
import shutil
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

try:
    from .models import ThreatResponse, DreadRequest, DreadResponse
    from .stride_agent import analyze_system_flow
except ImportError:
    from models import ThreatResponse, DreadRequest, DreadResponse
    from stride_agent import analyze_system_flow

from graphviz import Digraph

app = FastAPI()

# CORS (allow frontend to access backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for MVP
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backend running"}

@app.post("/analyze", response_model=ThreatResponse)
async def analyze_flow(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object.")

    if "flow" in payload:
        flow_data = payload["flow"]
    elif "nodes" in payload and "flows" in payload:
        flow_data = payload
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either a 'flow' field or a DFD JSON object with 'nodes' and 'flows'.",
        )

    if isinstance(flow_data, str) and not flow_data.strip():
        raise HTTPException(status_code=400, detail="'flow' must not be empty.")

    if not isinstance(flow_data, (str, dict, list)):
        raise HTTPException(
            status_code=400,
            detail="'flow' must be a string, object, or array.",
        )

    threats = analyze_system_flow(flow_data)
    return {"threats": threats}

@app.post("/dread", response_model=DreadResponse)
def calculate_overall_dread(dread: DreadRequest):
    # Validate that values are provided and within expected range (0-10)
    values = [
        dread.damage,
        dread.reproducibility,
        dread.exploitability,
        dread.affected_users,
        dread.discoverability
    ]
    # Basic validation
    if any(v is None for v in values):
        raise HTTPException(status_code=400, detail="All five DREAD values must be provided.")
    if any((not isinstance(v, (int, float)) or v < 0 or v > 10) for v in values):
        raise HTTPException(status_code=400, detail="DREAD values must be numbers between 0 and 10.")

    score = round(sum(values) / 5.0, 2)
    return {"score": score}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DFD_FOLDER = os.path.join(BASE_DIR, "dfds")
os.makedirs(DFD_FOLDER, exist_ok=True)


@app.post("/generate_dfd")
async def generate_dfd(request: Request):
    """
    Accepts JSON with 'nodes' and 'flows' describing the DFD,
    generates a PNG using graphviz, saves it in dfds/, and returns the image.
    Expected body:
    {
      "nodes": [{"id":"User","label":"User","type":"external_entity"}, ...],
      "flows": [{"source":"User","target":"AuthAPI","label":"Login","stride":["Spoofing"]}, ...]
    }
    """
    # 1) Check Graphviz 'dot' is available
    if shutil.which("dot") is None:
        raise HTTPException(
            status_code=500,
            detail="Graphviz 'dot' executable not found on server. Install Graphviz and ensure 'dot' is in PATH."
        )

    # 2) Load JSON
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object.")

    nodes = data.get("nodes", [])
    flows = data.get("flows", [])

    if not isinstance(nodes, list) or not isinstance(flows, list) or len(nodes) == 0 or len(flows) == 0:
        raise HTTPException(status_code=400, detail="Request JSON must include non-empty 'nodes' and 'flows' arrays.")

    # 3) Map node types to graphviz shapes (extendable)
    shape_map = {
        "external_entity": "oval",
        "process": "circle",
        "data_store": "box3d"
    }

    dot = Digraph(comment="Structured DFD", format="png")

    # 4) Add nodes
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            raise HTTPException(status_code=400, detail="Each node must have an 'id' field.")
        label = node.get("label", node_id)
        node_type = (node.get("type") or "").lower()
        shape = shape_map.get(node_type, "box")
        try:
            dot.node(node_id, label, shape=shape)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding node '{node_id}': {str(e)}")

    # 5) Add flows/edges
    for flow in flows:
        src = flow.get("source")
        tgt = flow.get("target")
        if not src or not tgt:
            raise HTTPException(status_code=400, detail="Each flow must include 'source' and 'target' fields.")
        label = flow.get("label", "")
        stride = flow.get("stride", [])
        if isinstance(stride, list) and len(stride) > 0:
            # append STRIDE tags on new line
            label = label + ("\n[" + ", ".join(stride) + "]")
        try:
            dot.edge(src, tgt, label=label)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding edge {src} -> {tgt}: {str(e)}")

    # 6) Render to file
    file_id = uuid.uuid4().hex
    filename = os.path.join(DFD_FOLDER, f"dfd_{file_id}")
    try:
        # render() will create filename.png
        dot.render(filename=filename, format="png", cleanup=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graphviz render failed: {str(e)}")

    image_path = f"{filename}.png"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=500, detail="DFD image file not found after render.")

    # 7) Return the image
    return FileResponse(image_path, media_type="image/png", filename=os.path.basename(image_path))
