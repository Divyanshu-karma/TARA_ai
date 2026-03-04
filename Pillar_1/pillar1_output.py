from services.classifier import classify
from services.interpreter import interpret_classification


def format_classification_output(result: dict) -> str:
    """
    Convert system classification JSON into a client-friendly message.
    """

    # Map system status → human language
    status_map = {
        "Valid": "Correct",
        "Invalid": "Likely incorrect"
    }

    claimed_class = result.get("claimedClass")
    status = status_map.get(result.get("claimedClassStatus"), result.get("claimedClassStatus"))
    suggested_class = result.get("suggestedClass")
    confidence = result.get("confidenceLevel")

    output = (
        f"Class Selected in trademark application: {claimed_class}\n"
        f"Assessment: {status}\n"
        f"Suggested Class: {suggested_class}\n"
        f"Confidence: {confidence}"
    )

    return output


if __name__ == "__main__":

    print("\nTEST CASE 3 — BORDERLINE CASE\n")

    raw_result = classify(
        class_number=39,
        identification="Retail store services featuring footwear, apparel, and streetwear, including products from nike, adidas, carhartt and other fashion brands stores"
    )

    final_result = interpret_classification(raw_result)

    formatted_output = format_classification_output(final_result)

    print(formatted_output)



# from services.classifier import classify
# from services.interpreter import interpret_classification

# if __name__ == "__main__":

#     print("\nTEST CASE 3 — BORDERLINE CASE\n")

#     raw_result = classify(
#         class_number=39,
#         identification="Retail store services featuring footwear, apparel, and streetwear, including products from nike, adidas, carhartt and other fashion brands stores"
#     )

#     final_result = interpret_classification(raw_result)
#     print(final_result)


# from services.classifier import classify
# from services.interpreter import interpret_classification

# if __name__ == "__main__":

#     raw_result = classify(
#         class_number=19,
#         identification="lace ribbons and embroidery for clothing decoration"
#     )

#     final_result = interpret_classification(raw_result)

#     print("\n=== CLASSIFICATION RESULT ===")
#     print(final_result)
# """
# main.py
# ========
# Primary API entry point for TMEP Assist Examination Engine.

# This file exposes clean callable functions for:
# - Pillar 1 only
# - Full 3-pillar pipeline
# - Future extension to §800, §704.02, §1200 etc.

# No CLI.
# No Streamlit.
# Pure orchestration layer.
# """

# from typing import Dict, Any

# from run_pipeline import run_full_pipeline
# from pillar1.service import run_pillar1


# # ─────────────────────────────────────────────
# # PILLAR 1 ONLY
# # ─────────────────────────────────────────────

# def assess_classification(application_dict: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Runs only Pillar 1 (§1401 Classification).
#     Used by Streamlit lightweight validation.
#     """
#     return run_pillar1(application_dict)


# # ─────────────────────────────────────────────
# # FULL ENGINE
# # ─────────────────────────────────────────────

# def assess_full_examination(application_dict: Dict[str, Any]):
#     """
#     Runs full 3-pillar structural examination.

#     Returns:
#         PipelineState
#     """
#     return run_full_pipeline(application_dict, save_result=True)