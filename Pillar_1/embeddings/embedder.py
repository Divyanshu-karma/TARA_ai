from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def embed(self, text: str):
        # BGE requires instruction prefix for better performance
        formatted_text = f"Represent this text for semantic similarity: {text}"
        return self.model.encode(formatted_text, normalize_embeddings=True).tolist()