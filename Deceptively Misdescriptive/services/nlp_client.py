import spacy
import re

class NLPClient:
    def __init__(self):
        # Load the small English NLP model
        self.nlp = spacy.load("en_core_web_sm")

    def split_mark_name(self, mark_name):
        """Splits CamelCase and spaces. 'ToppleWorld' -> ['Topple', 'World']"""
        # Add space between lower and upper case letters
        spaced_mark = re.sub(r'([a-z])([A-Z])', r'\1 \2', mark_name)
        return spaced_mark.split()

    def extract_core_goods(self, goods_services_text):
        """Extracts key noun phrases to create a clean, searchable list."""
        doc = self.nlp(goods_services_text.lower())
        
        # Extract noun chunks, filter out long phrases and noise words
        noise_words = {"services", "featuring", "products", "store"}
        core_nouns = []
        
        for chunk in doc.noun_chunks:
            words = chunk.text.split()
            # Keep short phrases and remove common noise
            if len(words) <= 3 and not any(noise in words for noise in noise_words):
                core_nouns.append(chunk.text)
                
        # Deduplicate and return a concise list (top 5 for search efficiency)
        return list(set(core_nouns))[:5]