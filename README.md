# STRIDE Threat Analyzer

This project analyzes system flows for STRIDE risks and can render a data flow diagram from JSON input. The backend uses FastAPI plus Gemini for threat analysis, and the frontend is a Vite/React app in `final-front/`.

## Features
- Analyze plain-text system descriptions or pasted JSON with Gemini.
- Generate a DFD image from JSON containing `nodes` and `flows`.
- Calculate an overall DREAD score.
- Return structured STRIDE threats from the backend.

## Project Structure
```text
threat-modelling/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── stride_agent.py
│   └── requirements.txt
└── final-front/
    ├── package.json
    └── src/
```

## Requirements
- Python 3.10+
- Node.js 18+
- A Gemini API key in `GEMINI_API_KEY`
- Graphviz installed on the machine, including the `dot` executable

## Backend Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

Set the Gemini key:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

Optional:
```bash
export GEMINI_MODEL="gemini-2.5-flash"
```

Start the API:
```bash
uvicorn backend.main:app --reload
```

The backend will be available at `http://127.0.0.1:8000`.

## Frontend Setup
```bash
cd final-front
npm install
npm run dev
```

Optional frontend API override:
```bash
export VITE_API_BASE_URL="http://127.0.0.1:8000"
```

## Input Formats

Threat analysis:
```json
{
  "flow": "A user logs into a banking app through an authentication API..."
}
```

DFD generation:
```json
{
  "nodes": [
    { "id": "User", "label": "User", "type": "external_entity" },
    { "id": "AuthAPI", "label": "Authentication API", "type": "process" }
  ],
  "flows": [
    { "source": "User", "target": "AuthAPI", "label": "Login Request", "stride": ["Spoofing"] }
  ]
}
```

## Notes
- The DFD endpoint does not call Gemini for image generation; it renders the diagram with Graphviz from the JSON you provide.
- If DFD generation fails, confirm both the Python `graphviz` package and the system `dot` binary are installed.
- The frontend `Generate DFD` button expects valid JSON in the textarea.
