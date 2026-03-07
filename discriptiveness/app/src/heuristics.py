import numpy as np

class DescriptivenessHeuristic:
    """
    Combines outputs from linguistic, embedding, and cross‑encoder modules
    to produce final descriptiveness and genericness scores.
    """

    def __init__(self, ling_analyzer, emb_similarity, cross_encoder, weights=None):
        self.ling = ling_analyzer
        self.emb = emb_similarity
        self.cross = cross_encoder
        # Default weights – can be tuned via validation
        self.weights = weights or {
            'linguistic': 0.25,
            'embedding_max_term': 0.25,
            'embedding_goods': 0.20,
            'cross_encoder': 0.30
        }

    def assess(self, mark, goods, goods_class=None, descriptive_terms=None):
        """
        Returns a dict with scores and reasons.
        """
        # 1. Linguistic features
        ling_feat = self.ling.analyze(mark, goods, goods_class)

        # Construct a linguistic score (example: weighted combination)
        ling_score = (
            (0.2 if ling_feat['pos']['adjective_count'] > 0 else 0) +
            0.3 * ling_feat['dictionary_word_ratio'] +
            0.2 * ling_feat['descriptive_keyword_overlap'] +
            0.2 * ling_feat['ngram_overlap_with_goods'] +
            (0.1 if ling_feat['has_descriptive_suffix'] else 0)
        )
        ling_score = min(1.0, ling_score)

        # 2. Embedding similarity to descriptive terms (if provided)
        emb_term_score = 0.0
        if descriptive_terms:
            emb_term_score = self.emb.max_similarity_to_terms(mark, descriptive_terms)

        # 3. Embedding similarity to goods (bi‑encoder)
        emb_goods_score = self.emb.similarity_to_goods_segments(mark, goods)

        # 4. Cross‑encoder score
        cross_score = self.cross.similarity(mark, goods)

        # Weighted combination
        descriptive_score = (
            self.weights['linguistic'] * ling_score +
            self.weights['embedding_max_term'] * emb_term_score +
            self.weights['embedding_goods'] * emb_goods_score +
            self.weights['cross_encoder'] * cross_score
        )

        # Genericness detection (simplified)
        generic_score = 0.0
        reasons = []

        # If the mark is a dictionary word and highly similar to goods, could be generic
        if ling_feat['dictionary_word_ratio'] > 0.8 and cross_score > 0.7:
            generic_score = 0.8
            reasons.append("High similarity to goods and common word – potential genericness")
        elif ling_feat['dictionary_word_ratio'] > 0.9:
            generic_score = 0.4
            reasons.append("All words are common dictionary terms")

        # If mark is a hyponym of a goods category? (could be added with WordNet)

        # Build explanation
        explanation = f"Descriptiveness score: {descriptive_score:.2f}. "
        if reasons:
            explanation += "Reasons: " + "; ".join(reasons)

        return {
            'descriptive_score': round(descriptive_score, 2),
            'generic_score': round(generic_score, 2),
            'reasons': reasons,
            'explanation': explanation,
            'details': {
                'linguistic': ling_feat,
                'embedding_term': emb_term_score,
                'embedding_goods': emb_goods_score,
                'cross_encoder': cross_score
            }
        }