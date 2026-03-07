import numpy as np
from sentence_transformers import SentenceTransformer, util
from nltk import sent_tokenize

class EmbeddingSimilarity:
    """
    Uses a sentence‑transformer model to compute semantic similarity between
    the mark and a list of descriptive terms, and also between mark and goods.
    """

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        # Cache for pre‑computed class centroids (optional)
        self.class_centroids = {}

    def encode(self, text):
        """Return embedding for a single text."""
        return self.model.encode(text, convert_to_tensor=True)

    def similarity(self, emb1, emb2):
        """Cosine similarity between two embeddings."""
        return float(util.cos_sim(emb1, emb2)[0][0])

    def max_similarity_to_terms(self, mark, descriptive_terms):
        """
        Compute the maximum cosine similarity between the mark embedding
        and each individual descriptive term's embedding.
        """
        if not descriptive_terms:
            return 0.0
        mark_emb = self.encode(mark)
        term_embs = self.encode(descriptive_terms)
        sims = util.cos_sim(mark_emb, term_embs)[0]
        return float(sims.max())

    def similarity_to_class_centroid(self, mark, class_terms):
        """
        Pre‑compute centroid for a class (average of all term embeddings)
        and compare mark against it. (Useful for speed when class_terms are static.)
        """
        if not class_terms:
            return 0.0
        # Create a key for the class (e.g., tuple of terms sorted)
        # For simplicity, we'll just compute on the fly; you can cache.
        term_embs = self.encode(class_terms)
        centroid = term_embs.mean(axis=0)
        mark_emb = self.encode(mark)
        return self.similarity(mark_emb, centroid)

    def similarity_to_goods(self, mark, goods):
        """
        Compute similarity between mark and goods using the bi‑encoder.
        This is a fast alternative to the cross‑encoder.
        """
        if not goods:
            return 0.0
        mark_emb = self.encode(mark)
        goods_emb = self.encode(goods)
        return self.similarity(mark_emb, goods_emb)

    def similarity_to_goods_segments(self, mark, goods):
        """
        Split goods into sentences and take the maximum similarity.
        """
        if not goods:
            return 0.0
        sentences = sent_tokenize(goods)
        if not sentences:
            return 0.0
        mark_emb = self.encode(mark)
        sent_embs = self.encode(sentences)
        sims = util.cos_sim(mark_emb, sent_embs)[0]
        return float(sims.max())