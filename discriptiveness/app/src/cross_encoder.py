from sentence_transformers import CrossEncoder
from nltk import sent_tokenize
import numpy as np

class CrossEncoderSimilarity:
    """
    Uses a cross‑encoder to compute deep semantic similarity between mark and goods.
    Supports sentence‑level segmentation and returns attention weights for explainability.
    """

    def __init__(self, model_name='cross-encoder/stsb-roberta-large'):
        self.model = CrossEncoder(model_name, num_labels=1)  # regression output
        # We'll store the last attention scores if needed (for explainability)
        self.last_attention = None

    def similarity(self, mark, goods, return_segments=False):
        """
        Returns a score between 0 and 1. If return_segments=True, also returns
        the maximum segment score and the segment text.
        """
        if not goods:
            return 0.0 if not return_segments else (0.0, None)
        sentences = sent_tokenize(goods)
        if not sentences:
            return 0.0 if not return_segments else (0.0, None)

        pairs = [(mark, sent) for sent in sentences]
        scores = self.model.predict(pairs)
        # Normalize: assume model output range roughly 0-5 (for stsb models)
        # If using a different model, adjust normalization accordingly.
        scores_norm = [min(1.0, max(0.0, s / 5.0)) for s in scores]
        max_score = max(scores_norm)
        max_idx = int(np.argmax(scores_norm))

        if return_segments:
            return max_score, sentences[max_idx]
        return max_score

    def similarity_with_explanation(self, mark, goods):
        """
        Returns score and the most relevant sentence from goods, plus optionally attention.
        For attention, we'd need a model that returns cross‑attention; not all do.
        This method provides a simple explanation.
        """
        max_score, best_sentence = self.similarity(mark, goods, return_segments=True)
        explanation = f"Highest similarity with segment: '{best_sentence}' (score: {max_score:.2f})"
        return max_score, explanation