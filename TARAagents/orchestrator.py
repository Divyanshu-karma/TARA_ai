import re
import json
import time

from agents.risk_analyzer import run_risk_analyzer
from agents.refusal_predictor import run_refusal_predictor
from agents.strategy_planner import run_strategy_planner
from agents.fix_generator import run_fix_generator


MAX_RETRIES = 2


# ---------------------------------
# JSON Parsing Utilities
# ---------------------------------

def safe_json_parse(text):
    """
    Try strict JSON parse first.
    If it fails, try extracting JSON block.
    If still fails, return raw text.
    """

    try:
        return json.loads(text)
    except Exception:
        pass

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return text
# ---------------------------------
# Safe Key Extractor
# ---------------------------------

def safe_get(data, key):
    """
    Safely extract a key from agent output.
    If output is not dict or key missing,
    return the raw data so pipeline continues.
    """

    if isinstance(data, dict):
        return data.get(key, data)

    return data



# ---------------------------------
# Agent Execution with Retry
# ---------------------------------

def run_agent_with_retry(agent_fn, payload, expected_key):

    for attempt in range(MAX_RETRIES + 1):

        try:
            result = agent_fn(payload)

            parsed = safe_json_parse(result)

            if isinstance(parsed, dict) and expected_key in parsed:
                return parsed
            if attempt == MAX_RETRIES:
                return parsed

        except Exception as e:
            print(f"Agent error: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(1)

    return result


# ---------------------------------
# Agent Pipeline
# ---------------------------------

def run_pipeline(report_json):

    print("Starting TARA agent pipeline")

    # --------------------
    # Agent 1 — Risk Analyzer
    # --------------------

    risk_payload = {
        "report_json": report_json
    }

    risk_output = run_agent_with_retry(
        run_risk_analyzer,
        risk_payload,
        "identified_risks"
    )

    print("Agent 1 completed")


    # --------------------
    # Agent 2 — Refusal Predictor
    # --------------------

    refusal_payload = {
        "report_json": report_json,
        "identified_risks": safe_get(risk_output, "identified_risks")
    }

    refusal_output = run_agent_with_retry(
        run_refusal_predictor,
        refusal_payload,
        "predicted_refusals"
    )

    print("Agent 2 completed")


    # --------------------
    # Agent 3 — Strategy Planner
    # --------------------

    strategy_payload = {
        "report_json": report_json,
        "identified_risks": safe_get(risk_output, "identified_risks"),
        "predicted_refusals": safe_get(refusal_output, "predicted_refusals")
    }

    strategy_output = run_agent_with_retry(
        run_strategy_planner,
        strategy_payload,
        "strategy_plan"
    )

    print("Agent 3 completed")


    # --------------------
    # Agent 4 — Fix Generator
    # --------------------

    fix_payload = {
        "report_json": report_json,
        "identified_risks": safe_get(risk_output, "identified_risks"),
        "predicted_refusals": safe_get(refusal_output, "predicted_refusals"),
        "strategy_plan": safe_get(strategy_output, "strategy_plan")
    }

    fix_output = run_agent_with_retry(
        run_fix_generator,
        fix_payload,
        "application_improvements"
    )

    print("Agent 4 completed")


    return {
         "agent1_output": risk_output,
         "agent2_output": refusal_output,
         "agent3_output": strategy_output,
         "agent4_output": fix_output
    }


# ---------------------------------
# Public API Function
# ---------------------------------

def run_tara_analysis(report_json):

    if not isinstance(report_json, dict):
        raise ValueError("report_json must be a dictionary")

    result = run_pipeline(report_json)

    return {
        "status": "success",
        "tara_analysis": result
    }