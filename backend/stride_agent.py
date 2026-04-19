import json
import os

try:
    from .models import Threat
except ImportError:
    from models import Threat

try:
    from google import genai as modern_genai
except ImportError:
    modern_genai = None


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

PROMPT_TEMPLATE = """
You are a security expert that performs STRIDE threat modeling.

Given the following system architecture description, identify potential threats using the STRIDE framework.

Return a JSON array of objects like:
[
  {{
    "component": "Login API",
    "type": "Tampering",
    "description": "The API may be vulnerable to input tampering such as SQL injection."
  }},
  ...
]

Important: Output ONLY the JSON. Do not include any explanation, markdown formatting, or code blocks.

System description:
{flow_text}
"""


def extract_json_block(text: str) -> str:
    """
    Attempt to extract a JSON array from a Gemini response, even if it's wrapped in markdown or extra text.
    """
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def normalize_flow_text(flow_input):
    if isinstance(flow_input, str):
        return flow_input
    if isinstance(flow_input, (dict, list)):
        return json.dumps(flow_input, indent=2)
    raise TypeError("System flow input must be a string, object, or array.")


def generate_with_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    if modern_genai is not None:
        client = modern_genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return (response.text or "").strip()

    try:
        import google.generativeai as legacy_genai
    except ImportError:
        legacy_genai = None

    if legacy_genai is not None:
        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return (getattr(response, "text", "") or "").strip()

    raise RuntimeError(
        "Gemini SDK is not installed. Install the backend dependencies from backend/requirements.txt."
    )


def analyze_system_flow(flow_text):
    flow_text = normalize_flow_text(flow_text)
    prompt = PROMPT_TEMPLATE.format(flow_text=flow_text)

    try:
        raw_text = generate_with_gemini(prompt)
        if not raw_text:
            raise RuntimeError("Gemini returned an empty response.")

        # Try to extract the JSON part
        cleaned_text = extract_json_block(raw_text)

        # Parse JSON
        threats_raw = json.loads(cleaned_text)
        if not isinstance(threats_raw, list):
            raise ValueError("Gemini response was not a JSON array.")

        threats = []
        for t in threats_raw:
            threats.append(
                Threat(
                    component=t.get("component", "Unknown"),
                    type=t.get("type", "Unknown"),
                    description=t.get("description", "No description"),
                )
            )
        return threats

    except json.JSONDecodeError as e:
        return [
            Threat(
                component="Error",
                type="Parsing",
                description=f"Invalid JSON returned by Gemini: {str(e)}",
            )
        ]

    except Exception as e:
        return [
            Threat(
                component="Error",
                type="ModelCall",
                description=f"Error during Gemini analysis: {str(e)}",
            )
        ]


if __name__ == "__main__":
    sample_input = """
    A user logs into an online banking app. The login request is sent to an authentication API, which verifies credentials and issues a session token. The user then transfers funds, which calls a backend service connected to a transaction database.
    """
    result = analyze_system_flow(sample_input)
    for r in result:
        print(r)
