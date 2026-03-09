import json
from pathlib import Path

from llm.model_loader import ask_llm


# ---------------------------------
# Load Prompt
# ---------------------------------

PROMPT_PATH = Path("prompts/risk_prompt.txt")


def load_system_prompt():

    if not PROMPT_PATH.exists():
        raise FileNotFoundError("risk_prompt.txt not found")

    return PROMPT_PATH.read_text()


# ---------------------------------
# Build Messages
# ---------------------------------

def build_messages(payload):

    system_prompt = load_system_prompt()

    report_json = payload.get("report_json")

    user_prompt = f"""
INPUT DATA

report_json:
{json.dumps(report_json, indent=2)}

Return ONLY valid JSON.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages


# ---------------------------------
# Agent Entry Function
# ---------------------------------

def run_risk_analyzer(payload):

    messages = build_messages(payload)

    response = ask_llm(messages)

    return response