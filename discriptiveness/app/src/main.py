import os
from .linguistic import LinguisticAnalyzer
from .embeddings import EmbeddingSimilarity
from .cross_encoder import CrossEncoderSimilarity
from .heuristics import DescriptivenessHeuristic

class TrademarkAnalyzer:
    """
    High-level API for trademark descriptiveness analysis.
    Initializes all sub-modules and provides a unified analyze() method.
    """

    def __init__(self, descriptive_keywords_path=None):
        """
        Args:
            descriptive_keywords_path: Path to JSON file with class‑specific descriptive terms.
        """
        # Ensure models are cached in the runtime disk (if not already set)
        if "HF_HOME" not in os.environ:
            os.environ["HF_HOME"] = "/tmp/huggingface"

        # Initialize sub-modules
        self.linguistic = LinguisticAnalyzer(descriptive_keywords_path)
        self.embedding = EmbeddingSimilarity()          # uses sentence-transformers
        self.cross_encoder = CrossEncoderSimilarity()
        self.heuristic = DescriptivenessHeuristic(
            self.linguistic,
            self.embedding,
            self.cross_encoder
        )

    def analyze(self, mark, goods, goods_class=None):
        """
        Perform full descriptiveness analysis.

        Args:
            mark (str): The trademark text.
            goods (str): Description of goods/services.
            goods_class (str, optional): USPTO class (e.g., "30").

        Returns:
            dict: Contains descriptive_score, generic_score, reasons, explanation, details.
        """
        # Load descriptive terms for the class (if any)
        descriptive_terms = None
        if goods_class and self.linguistic.descriptive_keywords:
            class_key = f"class_{goods_class.zfill(3)}"  # e.g., class_030
            descriptive_terms = self.linguistic.descriptive_keywords.get(class_key, [])

        # Run the heuristic assessment
        result = self.heuristic.assess(
            mark=mark,
            goods=goods,
            goods_class=goods_class,
            descriptive_terms=descriptive_terms
        )
        return result