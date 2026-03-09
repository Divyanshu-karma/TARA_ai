import json
import gradio as gr

from orchestrator import run_tara_analysis


# -----------------------------------
# Main Analysis Function
# -----------------------------------

def analyze_trademark(report_json):

    if not isinstance(report_json, dict):
        return {"status": "error", "message": "Invalid JSON input"}

    try:
        result = run_tara_analysis(report_json)

        return {
            "status": "success",
            "tara_analysis": result
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# -----------------------------------
# Example Input
# -----------------------------------

example_json = {
    "application_overview": {
        "serial_number": "97654321",
        "mark_text": "NOVA",
        "applicant_name": "Nova Corp LLC",
        "filing_date": "2024-03-15",
        "filing_basis": "1(b)",
        "classes": [9, 42],
        "identification": "Computer software for..."
    },
    "overall_assessment": {
        "risk_level": "LOW",
        "confidence_score": 0.80
    },
    "classification_analysis": {
        "claimed_class": 9,
        "suggested_class": 42,
        "status": "Valid",
        "confidence": "High"
    },
    "conflict_analysis": {
        "total_conflicts": 2,
        "high_risk_conflicts": 1,
        "sample_conflicts": [
            {
                "conflicting_mark": "NOVA TECH",
                "serial": "88123456",
                "risk": "HIGH",
                "similarity_score": 0.87
            }
        ]
    },
    "distinctiveness_analysis": {
        "descriptive_score": 0.42,
        "generic_score": 0.18
    },
    "validation_issues": []
}


# -----------------------------------
# Gradio UI
# -----------------------------------

with gr.Blocks(title="TARA AI Trademark Analyzer") as app:

    gr.Markdown("# TARA AI — Trademark Risk Analyzer")

    gr.Markdown(
        "Paste the structured trademark report JSON and run the analysis pipeline."
    )

    input_box = gr.JSON(
        label="Trademark Report JSON",
        value=example_json
    )

    run_button = gr.Button("Run TARA Analysis")

    output_box = gr.JSON(
        label="TARA AI Analysis Output"
    )

    run_button.click(
        fn=analyze_trademark,
        inputs=input_box,
        outputs=output_box,
        api_name="analyze_trademark"
    )


# -----------------------------------
# Launch
# -----------------------------------

app.launch(server_name="0.0.0.0", server_port=7860)