# # app/config.py
# app/config.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Locate .env in project root (conflict_check folder)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

ATOM_API_KEY = os.getenv("ATOM_API_KEY")
ATOM_USER_ID = os.getenv("ATOM_USER_ID")

ATOM_TRademark_SEARCH_URL = os.getenv(
    "ATOM_TRademark_SEARCH_URL",
    "https://www.atom.com/api/marketplace/trademark-search"
)

HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))
PAGE_SIZE = int(os.getenv("PAGE_SIZE", "50"))

# import os

# # read from environment; provide sensible defaults for local dev
# ATOM_API_KEY = os.getenv("ATOM_API_KEY")
# ATOM_USER_ID = os.getenv("ATOM_USER_ID")
# # Endpoint for Atom trademark search (docs). Use exactly this path.
# ATOM_TRademark_SEARCH_URL = os.getenv(
#     "ATOM_TRademark_SEARCH_URL",
#     "https://www.atom.com/api/marketplace/trademark-search"
# )

# # Networking / client settings
# HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))   # seconds
# PAGE_SIZE = int(os.getenv("PAGE_SIZE", "50"))
# # ATOM_API_KEY="4d8bf154eb56ebf4"
# # ATOM_USER_ID=3136871
# # ATOM_BASE_URL="https://www.atom.com/api/marketplace/trademark-search"