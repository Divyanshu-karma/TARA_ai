"""
TMEP §1207.01 — DuPont Factor 1: Similarity of the Marks

Upgraded with NLP (Sentence-BERT) for true semantic/translation matching 
and Double Metaphone for advanced phonetic matching.
"""

from __future__ import annotations
import re
import jellyfish
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from similarity.models import Factor1Score

# Load a lightweight, fast NLP model for semantic embeddings
# (This runs locally and downloads once)
NLP_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# ──────────────────────────────────────────────────────────────────────────────
# WEIGHTS WITHIN FACTOR 1
# ──────────────────────────────────────────────────────────────────────────────
_W_VISUAL   = 0.35
_W_PHONETIC = 0.35
_W_MEANING  = 0.30  # Increased weight now that we have true semantic matching

# Expanded weak words based on trademark examination practice
_WEAK_WORDS = {
    # Articles
    "THE", "A", "AN",
    # Conjunctions
    "AND", "OR", "BUT", "NOR", "YET", "SO",
    # Prepositions
    "OF", "FOR", "IN", "ON", "AT", "BY", "WITH", "TO", "FROM",
    "UPON", "INTO", "UPON", "VIA", "PER",
    # Business entity designators (common US and international)
    "CO", "COMPANY", "CORP", "CORPORATION", "INC", "INCORPORATED",
    "LLC", "LTD", "LIMITED", "LLP", "LP", "PLC", "SA", "AG", "GMBH",
    "BV", "NV", "PTY", "PTE", "SDN", "BHD",
    # Generic terms often considered weak
    "BRAND", "GROUP", "SERVICES", "SOLUTIONS", "TECHNOLOGIES",
    "INTERNATIONAL", "HOLDINGS", "ENTERPRISES", "INDUSTRIES",
}

def _filter_weak_words(text: str) -> str:
    """
    Remove weak words from a normalized trademark string.
    If after removal the string is empty, return the original.
    """
    words = text.split()
    core_words = [w for w in words if w not in _WEAK_WORDS]
    if not core_words:
        return text
    return " ".join(core_words)

# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────────────────────────────────────────

def score_factor1(applied_mark: str, conflicting_mark: str) -> Factor1Score:
    """Computes DuPont Factor 1 score using NLP and phonetic algorithms."""
    
    a = _normalise(applied_mark)
    b = _normalise(conflicting_mark)

    if not a or not b:
        return Factor1Score(notes="One or both marks are empty.")

    visual   = _visual_similarity(a, b)
    phonetic = _phonetic_similarity(a, b)
    meaning, dom_match = _meaning_similarity(a, b)

    # Dominant word match still provides a legal boost
    boost = 0.05 if dom_match else 0.0

    composite = min(1.0, (
        visual   * _W_VISUAL +
        phonetic * _W_PHONETIC +
        meaning  * _W_MEANING +
        boost
    ))

    notes = _build_notes(a, b, visual, phonetic, meaning, dom_match)

    return Factor1Score(
        visual_similarity   = round(visual,   3),
        phonetic_similarity = round(phonetic, 3),
        meaning_similarity  = round(meaning,  3),
        dominant_word_match = dom_match,
        composite_score     = round(composite, 3),
        notes               = notes,
    )

# ──────────────────────────────────────────────────────────────────────────────
# VISUAL SIMILARITY — Jaro-Winkler
# ──────────────────────────────────────────────────────────────────────────────

def _visual_similarity(a: str, b: str) -> float:
    """
    Uses Jaro-Winkler distance via the jellyfish library. 
    It heavily weights prefix matches, which aligns with trademark law 
    (consumers read left-to-right and focus on the first word).
    """
    return jellyfish.jaro_winkler_similarity(a, b)

# ──────────────────────────────────────────────────────────────────────────────
# PHONETIC SIMILARITY — Double Metaphone
# ──────────────────────────────────────────────────────────────────────────────

def _phonetic_similarity(a: str, b: str) -> float:
    """
    Uses Double Metaphone to encode words into their phonetic representations,
    then compares the similarity of those phonetic strings.
    """
    core_a = _filter_weak_words(a)
    core_b = _filter_weak_words(b)

    # Double metaphone returns a tuple of (primary, secondary) phonetic codes
    meta_a = jellyfish.metaphone(core_a)
    meta_b = jellyfish.metaphone(core_b)

    # Compare phonetic codes using Jaro-Winkler
    return jellyfish.jaro_winkler_similarity(meta_a, meta_b)

# ──────────────────────────────────────────────────────────────────────────────
# MEANING SIMILARITY — NLP Word Embeddings (SBERT)
# ──────────────────────────────────────────────────────────────────────────────

def _meaning_similarity(a: str, b: str) -> tuple[float, bool]:
    """
    Uses Sentence-BERT to convert marks into high-dimensional vectors, 
    then calculates Cosine Similarity. This catches synonyms and translations
    (e.g., "WOLF" vs "LUPO").
    """
    core_a = _filter_weak_words(a)
    core_b = _filter_weak_words(b)

    # 1. True Semantic Similarity via Cosine Similarity
    embeddings = NLP_MODEL.encode([core_a, core_b])
    cos_sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    
    # Normalize score (Cosine similarity ranges -1 to 1, we want 0 to 1)
    semantic_score = max(0.0, float(cos_sim))

    # 2. Dominant word exact match check (Legal requirement fallback)
    dominant_match = False

    words_a = core_a.split()
    words_b = core_b.split()

    if words_a and words_b and words_a[0] == words_b[0]:
        dominant_match = True

    return semantic_score, dominant_match

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Uppercase, strip punctuation, collapse spaces."""
    text = text.upper().strip()
    text = re.sub(r"[^A-Z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text)

def _build_notes(
    a: str, b: str, visual: float, phonetic: float, meaning: float, dom_match: bool
) -> str:
    parts = [f"Comparing '{a}' vs '{b}'."]
    
    if visual >= 0.85: parts.append("Visually highly similar.")
    elif visual >= 0.70: parts.append("Visually moderately similar.")
    
    if phonetic >= 0.85: parts.append("Phonetically highly similar.")
    elif phonetic >= 0.70: parts.append("Phonetically moderately similar.")

    if dom_match:
        parts.append("Dominant word is identical.")
    elif meaning >= 0.75:
        parts.append("Strong semantic/conceptual similarity detected via NLP.")

    return " ".join(parts)