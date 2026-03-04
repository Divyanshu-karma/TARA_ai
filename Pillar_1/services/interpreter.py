def interpret_classification(result: dict) -> dict:
    """
    Improved multi-factor interpretation logic.
    """

    declared = result["declaredClass"]
    predicted = result["bestPredictedClass"]
    dominance = result["dominance"]
    declared_score = result["declaredScore"]
    predicted_score = result["bestPredictedScore"]

    # === Tunable thresholds ===
    STRONG_ALIGNMENT = 0.85
    MODERATE_ALIGNMENT = 0.75

    STRONG_DOMINANCE = 0.08
    MODERATE_DOMINANCE = 0.04

    NOISE_TOLERANCE = 0.02  # treat very small differences as tie

    # === Decision Logic ===

    # 1️⃣ If declared class is also best predicted
    if declared == predicted:

        if declared_score >= STRONG_ALIGNMENT:
            status = "Valid"
            confidence = "High"
            message = "The claimed class strongly aligns with the description."

        elif declared_score >= MODERATE_ALIGNMENT:
            status = "Valid"
            confidence = "Moderate"
            message = "The claimed class reasonably aligns with the description."

        else:
            status = "Borderline"
            confidence = "Low"
            message = "The claimed class alignment is weak and may require review."

    # 2️⃣ If another class slightly stronger (but within noise range)
    elif abs(dominance) <= NOISE_TOLERANCE:
        status = "Valid"
        confidence = "Moderate"
        message = "The claimed class is nearly equal in similarity to another competing class."

    # 3️⃣ If declared class moderately weaker
    elif -MODERATE_DOMINANCE <= dominance < -NOISE_TOLERANCE:
        status = "Borderline"
        confidence = "Low"
        message = "Another class shows slightly stronger semantic alignment."

    # 4️⃣ Strong misclassification
    elif dominance < -MODERATE_DOMINANCE:
        status = "Invalid"
        confidence = "High"
        message = "The claimed class does not align strongly with the description."

    # 5️⃣ Declared strongly dominant
    elif dominance >= STRONG_DOMINANCE:
        status = "Valid"
        confidence = "High"
        message = "The claimed class clearly dominates competing classes."

    else:
        status = "Valid"
        confidence = "Moderate"
        message = "The claimed class aligns with the description."

    return {
        "claimedClass": declared,
        "claimedClassStatus": status,
        "suggestedClass": predicted if status == "Invalid" else declared,
        "confidenceLevel": confidence,
        "explanation": message,
        "scores": {
            "claimedClassScore": round(declared_score, 4),
            "bestClassScore": round(predicted_score, 4),
            "dominanceMargin": round(dominance, 4)
        }
    }







# def interpret_classification(result: dict) -> dict:
#     """
#     Converts raw classifier output into user-friendly explanation.
#     """

#     declared = result["declaredClass"]
#     predicted = result["bestPredictedClass"]
#     dominance = result["dominance"]
#     declared_score = result["declaredScore"]
#     predicted_score = result["bestPredictedScore"]

#     # Threshold logic
#     STRONG_THRESHOLD = 0.08
#     BORDERLINE_THRESHOLD = 0.04

#     if dominance >= STRONG_THRESHOLD:
#         status = "Valid"
#         message = "The claimed class aligns strongly with the goods/services description."
#         confidence = "High"

#     elif 0 <= dominance < STRONG_THRESHOLD:
#         status = "Possibly Valid"
#         message = "The claimed class aligns with the description, but competing classes show some similarity."
#         confidence = "Moderate"

#     elif -BORDERLINE_THRESHOLD <= dominance < 0:
#         status = "Borderline"
#         message = "The claimed class is slightly weaker than a competing class."
#         confidence = "Low"

#     else:
#         status = "Invalid"
#         message = "The claimed class does not align strongly with the goods/services description."
#         confidence = "High"

#     return {
#         "claimedClass": declared,
#         "claimedClassStatus": status,
#         "suggestedClass": predicted if status == "Invalid" else declared,
#         "confidenceLevel": confidence,
#         "explanation": message,
#         "scores": {
#             "claimedClassScore": round(declared_score, 4),
#             "suggestedClassScore": round(predicted_score, 4),
#             "dominanceMargin": round(dominance, 4)
#         }
#     }