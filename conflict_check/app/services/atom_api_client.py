# app/services/atom_api_client.py

from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app import config
import logging

logger = logging.getLogger(__name__)


class AtomAPIError(Exception):
    pass


class AtomAPIClient:

    ALLOWED_FILING_STATUS = {"active", "pending", "dead", "all"}
    ALLOWED_SEARCH_TYPE = {"exact", "phrase", "broad"}

    def __init__(self):
        self.base_url = config.ATOM_TRademark_SEARCH_URL
        self.api_token = config.ATOM_API_KEY
        self.user_id = config.ATOM_USER_ID
        self.timeout = config.HTTP_TIMEOUT

        if not self.api_token or not self.user_id:
            raise ValueError(
                "ATOM_API_KEY and ATOM_USER_ID must be set in config or environment"
            )

        self.session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
        )

        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    # --------------------------------------------------
    # Internal Request Layer
    # --------------------------------------------------
    def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:

        try:
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "TrademarkConflictChecker/1.0",
                },
            )
        except requests.RequestException as e:
            logger.exception("Network error calling Atom API")
            raise AtomAPIError(str(e))

        if response.status_code == 429:
            raise AtomAPIError("Rate limited by Atom API (429)")

        if response.status_code >= 400:
            raise AtomAPIError(
                f"Atom API HTTP {response.status_code}: {response.text}"
            )

        try:
            return response.json()
        except ValueError:
            raise AtomAPIError("Invalid JSON response from Atom API")

    # --------------------------------------------------
    # Public Single Page Fetch
    # --------------------------------------------------
    def search_trademark_page(
        self,
        keyword: str,
        intl_class: str = None,
        filing_status: str = "all",
        search_type: str = "broad",
        page: int = 1,
        page_size: int = 100,  # default to max allowed
    ) -> Dict[str, Any]:

        if not keyword:
            raise ValueError("keyword is required")

        if search_type not in self.ALLOWED_SEARCH_TYPE:
            raise ValueError(
                f"search_type must be one of {self.ALLOWED_SEARCH_TYPE}"
            )

        if filing_status not in self.ALLOWED_FILING_STATUS:
            raise ValueError(
                f"filing_status must be one of {self.ALLOWED_FILING_STATUS}"
            )

        params = {
            "api_token": self.api_token,
            "user_id": self.user_id,
            "keyword": keyword,
            "search_type": search_type,
            "filing_status": filing_status,
            "page": page,
            "page_size": page_size,
        }

        if intl_class:
            params["class"] = str(intl_class).zfill(3)

        logger.debug("Atom search params: %s", params)

        # 🔥 ALWAYS return full JSON payload
        return self._request(params)















# # app/services/atom_api_client.py


# from typing import Dict, Any, Generator
# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# from app import config
# import time
# import logging

# logger = logging.getLogger(__name__)


# class AtomAPIError(Exception):
#     pass


# class AtomAPIClient:
#     BASE_URL = "https://www.atom.com/api/marketplace/trademark-search"

#     ALLOWED_FILING_STATUS = {"active", "pending", "dead", "all"}
#     ALLOWED_SEARCH_TYPE = {"exact", "phrase", "broad"}

#     def __init__(self):
#         self.api_token = config.ATOM_API_KEY
#         self.user_id = config.ATOM_USER_ID
#         self.timeout = config.HTTP_TIMEOUT

#         if not self.api_token or not self.user_id:
#             raise ValueError(
#                 "ATOM_API_KEY and ATOM_USER_ID must be set in config or environment"
#             )

#         # keep retry logic (good practice)
#         self.session = requests.Session()
#         retries = Retry(
#             total=3,
#             backoff_factor=0.8,
#             status_forcelist=(429, 500, 502, 503, 504),
#             allowed_methods=frozenset(["GET"])
#         )
#         self.session.mount("https://", HTTPAdapter(max_retries=retries))

#     # ---------------------------
#     # Internal request wrapper
#     # ---------------------------
#     def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         try:
#             response = self.session.get(
#                 self.BASE_URL,
#                 params=params,
#                 timeout=self.timeout,
#                 headers={
#                     "Accept": "application/json",
#                     "User-Agent": "TrademarkConflictChecker/1.0"
#                 }
#             )
#         except requests.RequestException as e:
#             logger.exception("Network error calling Atom API")
#             raise AtomAPIError(str(e))

#         if response.status_code == 429:
#             raise AtomAPIError("Rate limited by Atom API (429)")

#         if response.status_code >= 400:
#             raise AtomAPIError(
#                 f"Atom API HTTP {response.status_code}: {response.text}"
#             )

#         try:
#             return response.json()
#         except ValueError:
#             raise AtomAPIError("Invalid JSON response from Atom API")

#     # ---------------------------
#     # Single page search
#     # ---------------------------
#     def search_trademark_page(
#         self,
#         keyword: str,
#         intl_class: str = None,
#         filing_status: str = "all",
#         search_type: str = "broad",
#         page: int = 1,
#     ) -> Dict[str, Any]:

#         if search_type not in self.ALLOWED_SEARCH_TYPE:
#             raise ValueError(
#                 f"search_type must be one of {self.ALLOWED_SEARCH_TYPE}"
#             )

#         if filing_status not in self.ALLOWED_FILING_STATUS:
#             raise ValueError(
#                 f"filing_status must be one of {self.ALLOWED_FILING_STATUS}"
#             )

#         if not keyword:
#             raise ValueError("keyword is required")

#         params = {
#             "api_token": self.api_token,  # REQUIRED
#             "user_id": self.user_id,      # REQUIRED
#             "keyword": keyword,
#             "search_type": search_type,
#             "filing_status": filing_status,
#             "page": page,
#         }

#         if intl_class:
#             params["class"] = str(intl_class).zfill(3)  # ensure 025 format

#         logger.debug("Atom search params: %s", params)

#         return self._request(params)

#     # ---------------------------
#     # Multi-page generator
#     # ---------------------------
#     def search_trademark(
#         self,
#         keyword: str,
#         intl_class: str = None,
#         filing_status: str = "all",
#         search_type: str = "broad",
#         max_pages: int = 5,
#     ) -> Generator[Dict[str, Any], None, None]:

#         page = 1

#         while page <= max_pages:
#             payload = self.search_trademark_page(
#                 keyword=keyword,
#                 intl_class=intl_class,
#                 filing_status=filing_status,
#                 search_type=search_type,
#                 page=page,
#             )

#             # Swagger shows array response, not wrapped in "results"
#             if isinstance(payload, list):
#                 items = payload
#             else:
#                 items = payload.get("results") or payload.get("data") or []

#             if not items:
#                 break

#             for item in items:
#                 yield item

#             page += 1
#             time.sleep(0.2)  # polite delay


















# from typing import Dict, Any, Generator
# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# from app import config
# import time
# import logging

# logger = logging.getLogger(__name__)

# class AtomAPIError(Exception):
#     pass

# class AtomAPIClient:
#     def __init__(self):
#         self.base_url = config.ATOM_TRademark_SEARCH_URL
#         self.api_token = config.ATOM_API_KEY
#         self.user_id = config.ATOM_USER_ID
#         self.timeout = config.HTTP_TIMEOUT

#         self.session = requests.Session()
#         retries = Retry(
#             total=3,
#             backoff_factor=0.8,
#             status_forcelist=(429, 500, 502, 503, 504),
#             allowed_methods=frozenset(["GET", "POST"])
#         )
#         self.session.mount("https://", HTTPAdapter(max_retries=retries))

#         if not self.api_token or not self.user_id:
#             raise ValueError("ATOM_API_KEY and ATOM_USER_ID must be set in config or environment")

#     def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         try:
#             # r = self.session.get(self.base_url, params=params, timeout=self.timeout)
#             r = self.session.get(
#                 self.base_url,
#                 params=params,
#                 timeout=self.timeout,
#                 headers={
#                     "Accept": "application/json",
#                     "User-Agent": "TrademarkConflictChecker/1.0"
#                 }
#             )
#         except requests.RequestException as e:
#             logger.exception("Network error calling Atom API")
#             raise AtomAPIError(str(e))

#         if r.status_code == 429:
#             # polite backoff; Retry adapter will already do several attempts
#             raise AtomAPIError("Rate limited by Atom API (429)")
#         if r.status_code >= 400:
#             raise AtomAPIError(f"Atom API HTTP {r.status_code}: {r.text}")

#         try:
#             return r.json()
#         except ValueError:
#             raise AtomAPIError("Invalid JSON response from Atom API")

#     def search_trademark_page(self, keyword: str, intl_class: str = None,
#                               filing_status: str = None, search_type: str = None,
#                               page: int = 1, page_size: int = None) -> Dict[str, Any]:
#         if page_size is None:
#             page_size = config.PAGE_SIZE

#         params = {
#             "api_token": self.api_token,
#             "user_id": self.user_id,
#             "keyword": keyword,
#             "page": page,
#             "page_size": page_size
#         }
#         if intl_class:
#             params["class"] = str(intl_class)
#         if filing_status:
#             params["filing_status"] = filing_status
#         if search_type:
#             params["search_type"] = search_type

#         logger.debug("Atom search params: %s", params)
#         return self._request(params)

#     def search_trademark(self, keyword: str, intl_class: str = None,
#                          filing_status: str = None, search_type: str = None,
#                          max_pages: int = 10) -> Generator[Dict[str, Any], None, None]:
#         """Yield items across pages (generator)."""
#         page = 1
#         while True:
#             payload = self.search_trademark_page(keyword, intl_class, filing_status, search_type, page)
#             # assume results are in payload['results'] or payload['data'] — be defensive
#             items = payload.get("results") or payload.get("data") or []
#             if not items:
#                 break
#             for it in items:
#                 yield it
#             # determine if more pages exist
#             # Many Atom endpoints include total/pages; fallback to stopping on empty page
#             total_pages = payload.get("total_pages") or payload.get("pages") or None
#             if total_pages:
#                 if page >= int(total_pages) or page >= max_pages:
#                     break
#             page += 1
#             if page > max_pages:
#                 break
#             # small polite delay
#             time.sleep(0.1)


# # # app/services/atom_api_client.py

# # import requests
# # from app.config import ATOM_API_KEY, ATOM_BASE_URL, ATOM_USER_ID

# # class AtomAPIClient:
# #     def search_trademark(self, keyword, intl_class=None, filing_status=None, search_type=None):
# #         params = {
# #             "api_token": ATOM_API_KEY,  # required
# #             "user_id": ATOM_USER_ID,    # required
# #             "keyword": keyword          # required
# #         }

# #         # if optional filters provided
# #         if intl_class:
# #             params["class"] = intl_class

# #         if filing_status:
# #             params["filing_status"] = filing_status

# #         if search_type:
# #             params["search_type"] = search_type

# #         response = requests.get(ATOM_BASE_URL, params=params)

# #         # simple error raising
# #         if response.status_code != 200:
# #             raise Exception(f"Atom API Error {response.status_code}: {response.text}")

# #         return response.json()
# # # import requests
# # # from app.config import ATOM_API_KEY, ATOM_BASE_URL


# # # class AtomAPIClient:
# # #     def search_trademark(self, keyword, intl_class=None, filing_status=None):
# # #         params = {
# # #             "api_token": ATOM_API_KEY,
# # #             "keyword": keyword
# # #         }

# # #         # Only add optional filters if provided
# # #         if intl_class:
# # #             params["class"] = intl_class

# # #         if filing_status:
# # #             params["filing_status"] = filing_status

# # #         response = requests.get(ATOM_BASE_URL, params=params)

# # #         # Debug-safe handling
# # #         if response.status_code != 200:
# # #             raise Exception(
# # #                 f"Atom API Error {response.status_code}: {response.text}"
# # #             )

# # #         # Ensure response is JSON
# # #         try:
# # #             return response.json()
# # #         except ValueError:
# # #             raise Exception(
# # #                 f"Invalid JSON response from Atom API: {response.text}"
# # #             )