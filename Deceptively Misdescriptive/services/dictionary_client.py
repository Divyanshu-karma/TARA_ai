# dictionary_client.py
import requests

class DictionaryClient:
    def get_definition(self, term):
        """Fetches definition from Free Dictionary API."""
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Extract the first definition found
                return data[0]['meanings'][0]['definitions'][0]['definition']
            return None
        except Exception:
            return None