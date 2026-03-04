import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("ATOM_API_KEY")
USER_ID = os.getenv("ATOM_USER_ID")

url = "https://www.atom.com/api/marketplace/trademark-search"

params = {
    "api_token": API_KEY,
    "user_id": USER_ID,
    "keyword": "NIKE"
}

response = requests.get(
    url,
    params=params,
    headers={
        "Accept": "application/json",
        "User-Agent": "TrademarkConflictChecker/1.0"
    },
    timeout=10
)

print("STATUS:", response.status_code)
print("RESPONSE:")
print(response.text[:1000])

from app.utils.extract_pairs import iterate_pairs_from_file

print("\n----- TESTING JSON PARSER -----\n")

# path to one json file
file_path = Path("search_data/search_TESLA_20260304_031319.json")

for name, serial, idx in iterate_pairs_from_file(file_path):

    print("Index:", idx)
    print("Trademark:", name)
    print("Serial:", serial)
    print("--------------------")