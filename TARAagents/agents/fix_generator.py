import json
from pathlib import Path

from llm.model_loader import ask_llm


# ---------------------------------
# Load System Prompt
# ---------------------------------

PROMPT_PATH = Path("prompts/fix_prompt.txt")


def load_system_prompt():

    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            "fix_prompt.txt not found in prompts folder"
        )

    return PROMPT_PATH.read_text()


# ---------------------------------
# Build Chat Messages
# ---------------------------------

def build_messages(payload):

    system_prompt = load_system_prompt()

    report_json = payload.get("report_json")
    risks = payload.get("identified_risks")
    refusals = payload.get("predicted_refusals")
    strategy_plan = payload.get("strategy_plan")

    user_prompt = f"""
INPUT DATA

report_json:
{json.dumps(report_json, indent=2)}

identified_risks:
{json.dumps(risks, indent=2)}

predicted_refusals:
{json.dumps(refusals, indent=2)}

strategy_plan:
{json.dumps(strategy_plan, indent=2)}

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

def run_fix_generator(payload):
    """
    Executes Application Fix Generator Agent.

    Expected payload:
    {
        "report_json": {...},
        "identified_risks": [...],
        "predicted_refusals": [...],
        "strategy_plan": [...]
    }

    Returns raw JSON string.
    """

    messages = build_messages(payload)

    response = ask_llm(messages)

    return response