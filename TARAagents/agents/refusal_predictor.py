import json
from pathlib import Path

from llm.model_loader import ask_llm


# ---------------------------------
# Load System Prompt
# ---------------------------------

PROMPT_PATH = Path("prompts/refusal_prompt.txt")


def load_system_prompt():

    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            "refusal_prompt.txt not found in prompts folder"
        )

    return PROMPT_PATH.read_text()


# ---------------------------------
# Build Chat Messages
# ---------------------------------

def build_messages(payload):

    system_prompt = load_system_prompt()

    report_json = payload.get("report_json")
    identified_risks = payload.get("identified_risks")

    user_prompt = f"""
INPUT DATA

report_json:
{json.dumps(report_json, indent=2)}

identified_risks:
{json.dumps(identified_risks, indent=2)}

Return ONLY valid JSON.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    return messages


# ---------------------------------
# Agent Entry Function
# ---------------------------------

def run_refusal_predictor(payload):
    """
    Executes Refusal Predictor Agent.

    Expected payload:
    {
        "report_json": {...},
        "identified_risks": [...]
    }

    Returns raw JSON string from LLM.
    """

    messages = build_messages(payload)

    response = ask_llm(messages)

    return response