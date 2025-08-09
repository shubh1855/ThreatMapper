import cohere
import os
import json

# Initialize Cohere client with API key from environment variable
co = cohere.Client(os.environ["COHERE_API_KEY"])

PROMPT_TEMPLATE = """
You are a cybersecurity assistant that performs STRIDE threat modeling.

Given this system description:

{system_flow}

1. Identify system components.
2. Identify trust boundaries.
3. Apply STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) to each component.
4. Output ONLY a JSON array of objects in the format:
[
  {{
    "component": "Component Name",
    "type": "Threat Type",
    "description": "Short threat description"
  }}
]
Ensure the JSON is valid and does not contain extra text.
"""

def analyze_system_flow(flow_text: str):
    prompt = PROMPT_TEMPLATE.format(system_flow=flow_text)
    
    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=500,
        temperature=0.2
    )

    try:
        threats_json = json.loads(response.generations[0].text.strip())
        return threats_json
    except json.JSONDecodeError:
        # Fallback if AI doesn't return proper JSON
        return [{
            "component": "Error",
            "type": "Output Parsing",
            "description": f"Invalid JSON returned: {response.generations[0].text}"
        }]
