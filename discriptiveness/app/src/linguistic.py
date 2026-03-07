import spacy
import json
import os
import math
from collections import Counter
from nltk import word_tokenize
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import NOUN, ADJ, ADV, VERB

# Load spaCy model (download if not present: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

# Optional: load word frequency data (e.g., SUBTLEX frequency file)
# If not available, we use a simple fallback (all words equally frequent).
FREQ_DICT = {}
FREQ_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'word_freq.json')
if os.path.exists(FREQ_PATH):
    with open(FREQ_PATH, 'r') as f:
        FREQ_DICT = json.load(f)

class LinguisticAnalyzer:
    """
    Extracts rich linguistic features from a trademark string.
    Features include POS tags, dependency relations, dictionary membership,
    word frequency, n‑gram overlap with goods description, and named entities.
    """

    def __init__(self, descriptive_keywords_path=None):
        self.descriptive_keywords = {}
        if descriptive_keywords_path and os.path.exists(descriptive_keywords_path):
            with open(descriptive_keywords_path, 'r', encoding='utf-8') as f:
                self.descriptive_keywords = json.load(f)  # e.g., {"class_030": ["fresh", "creamy"]}

        # List of common descriptive suffixes (e.g., -y, -er, -ing)
        self.descriptive_suffixes = ('y', 'er', 'ing', 'ive', 'ous', 'al', 'ic')

    def pos_tags(self, text):
        """Return list of (token, POS, detailed tag) using spaCy."""
        doc = nlp(text)
        return [(token.text, token.pos_, token.tag_) for token in doc]

    def dependency_relations(self, text):
        """Extract adjective‑noun and other modifier relations."""
        doc = nlp(text)
        modifiers = []
        for token in doc:
            # amod: adjectival modifier, nmod: nominal modifier
            if token.dep_ in ('amod', 'nmod') and token.head.pos_ in ('NOUN', 'PROPN'):
                modifiers.append((token.text, token.head.text, token.dep_))
        return modifiers

    def is_dictionary_word(self, word):
        """Check if word exists in WordNet."""
        return bool(wordnet.synsets(word))

    def word_frequency(self, word):
        """
        Return log frequency of word (if available). Higher = more common.
        Defaults to 0 if not in frequency dictionary.
        """
        return FREQ_DICT.get(word.lower(), 0)

    def extract_ngrams(self, text, n=2, use_words=True):
        """Generate word n‑grams or character n‑grams."""
        if use_words:
            words = word_tokenize(text.lower())
            ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        else:
            # character n‑grams
            text_clean = text.lower().replace(' ', '')
            ngrams = [text_clean[i:i+n] for i in range(len(text_clean)-n+1)]
        return ngrams

    def ngram_overlap_with_goods(self, mark, goods, n=2):
        """
        Compute the fraction of mark word n‑grams that appear verbatim in the goods description.
        """
        if not goods:
            return 0.0
        mark_ngrams = set(self.extract_ngrams(mark, n=n, use_words=True))
        goods_ngrams = set(self.extract_ngrams(goods, n=n, use_words=True))
        if not mark_ngrams:
            return 0.0
        overlap = mark_ngrams.intersection(goods_ngrams)
        return len(overlap) / len(mark_ngrams)

    def descriptive_keyword_overlap(self, mark, goods_class=None):
        """
        Return fraction of mark words that appear (as lemmas) in the descriptive list for the given class.
        Uses lemmatization to catch inflected forms.
        """
        if not self.descriptive_keywords or not goods_class:
            return 0.0
        # Lemmatize mark words
        doc = nlp(mark)
        mark_lemmas = {token.lemma_.lower() for token in doc if token.is_alpha}
        desc_words = set(self.descriptive_keywords.get(goods_class, []))
        if not mark_lemmas or not desc_words:
            return 0.0
        overlap = mark_lemmas.intersection(desc_words)
        return len(overlap) / len(mark_lemmas)

    def has_descriptive_suffix(self, word):
        """Check if word ends with a common descriptive suffix."""
        return any(word.lower().endswith(suf) for suf in self.descriptive_suffixes)

    def extract_entities(self, text):
        """Return list of named entities (PERSON, ORG, GPE, etc.)."""
        doc = nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def analyze(self, mark, goods=None, goods_class=None):
        """
        Main method: returns a dictionary of linguistic features.
        """
        doc = nlp(mark)
        tokens = [token.text.lower() for token in doc if token.is_alpha]
        if not tokens:
            return {'pos': {}, 'dictionary_word_ratio': 0, 'avg_word_freq': 0,
                    'descriptive_keyword_overlap': 0, 'ngram_overlap_with_goods': 0,
                    'has_descriptive_suffix': False, 'has_entity': False, 'ngrams': []}

        # POS summary
        pos_tags = [(token.text, token.pos_, token.tag_) for token in doc]
        pos_summary = {
            'adjective_count': sum(1 for _, pos, _ in pos_tags if pos == 'ADJ'),
            'comparative_count': sum(1 for _, _, tag in pos_tags if tag in ('JJR', 'JJS')),
            'noun_count': sum(1 for _, pos, _ in pos_tags if pos == 'NOUN'),
            'verb_count': sum(1 for _, pos, _ in pos_tags if pos == 'VERB')
        }

        # Dependency modifiers
        modifiers = self.dependency_relations(mark)

        # Dictionary word ratio
        dict_word_ratio = sum(1 for w in tokens if self.is_dictionary_word(w)) / len(tokens) if tokens else 0

        # Average word frequency (log)
        avg_freq = sum(self.word_frequency(w) for w in tokens) / len(tokens) if tokens else 0

        # Overlap with goods n‑grams
        ngram_overlap = self.ngram_overlap_with_goods(mark, goods, n=2) if goods else 0.0

        # Descriptive keyword overlap (lemma‑based)
        desc_overlap = self.descriptive_keyword_overlap(mark, goods_class)

        # Suffix check on the longest word (or any)
        has_desc_suffix = any(self.has_descriptive_suffix(w) for w in tokens)

        # Named entities
        entities = self.extract_entities(mark)
        has_entity = len(entities) > 0

        # Word n‑grams for later use
        ngrams = self.extract_ngrams(mark, n=2, use_words=True)

        return {
            'pos': pos_summary,
            'modifiers': modifiers,
            'dictionary_word_ratio': dict_word_ratio,
            'avg_word_freq': avg_freq,
            'descriptive_keyword_overlap': desc_overlap,
            'ngram_overlap_with_goods': ngram_overlap,
            'has_descriptive_suffix': has_desc_suffix,
            'has_entity': has_entity,
            'ngrams': ngrams
        }