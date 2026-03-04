from pathlib import Path
# from app.similarity.dupont_engine import score_similarity
from app.services.response_parser import normalize_item
from app.services.atom_api_client import AtomAPIClient
from typing import List
import json
import os
from datetime import datetime
from math import ceil

class TrademarkSearchService:
    def __init__(self):
        self.client = AtomAPIClient()
    def search(
        self,
        keyword: str,
        intl_class: str = None,
        filing_status: str = None,
        max_pages: int = 3,
        page_size: int = 100
    ):

        all_raw_items = []
        all_records = []

        print(f"\nSearching '{keyword}' (class={intl_class}, status={filing_status})")

        for page in range(1, max_pages + 1):

            print(f"Fetching page {page}")

            payload = self.client.search_trademark_page(
                keyword=keyword,
                intl_class=intl_class,
                filing_status=filing_status,
                page=page,
                page_size=page_size
            )

            items = payload.get("results") or payload.get("data") or []

            if not items:
                break

            for item in items:
                all_raw_items.append(item)

                record = normalize_item(item)
                all_records.append(record)

    # save raw Atom results
        self._store_search_data(keyword, all_raw_items)

        return all_records



    # def search(
    #     self,
    #     keyword: str,
    #     intl_class: str = None,
    #     filing_status: str = None,
    #     max_pages: int = 3,          # Fetch only first 3 pages
    #     page_size: int = 100,        # Platform max
    #     high_conflict_threshold: float = 0.85
    # ):

    #     all_raw_items = []
    #     all_records = []

    #     print(f"\nSearching '{keyword}' (class={intl_class}, status={filing_status})")
    #     print(f"Max pages: {max_pages}, Page size: {page_size}")

    #     for page in range(1, max_pages + 1):

    #         print(f"\nFetching page {page}...")

    #         payload = self.client.search_trademark_page(
    #             keyword=keyword,
    #             intl_class=intl_class,
    #             filing_status=filing_status,
    #             page=page,
    #             page_size=page_size
    #         )

    #         total_results = payload.get("total_results", 0)
    #         items = payload.get("results") or payload.get("data") or []

    #         if page == 1:
    #             print(f"Total results in Atom DB: {total_results}")

    #         if not items:
    #             print("No more results.")
    #             break

    #         for item in items:
    #             all_raw_items.append(item)

    #             record = normalize_item(item)

    #             # sim_score = score_similarity(keyword, record.mark_text or "")
    #             # record.raw["similarity_score"] = sim_score

    #             all_records.append(record)

    #         # 🔥 EARLY STOP if very high similarity found
    #             if sim_score >= high_conflict_threshold:
    #                 print(f"\n🚨 High conflict found: {record.mark_text} (score={sim_score})")
    #                 self._store_search_data(keyword, all_raw_items)
    #                 return all_records

    # # Save fetched pages
    #     self._store_search_data(keyword, all_raw_items)

    #     return all_records

    
    def _store_search_data(self, keyword: str, data: list):

        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        folder = BASE_DIR / "search_data"
        folder.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = folder / f"search_{keyword}_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n📁 Saved ALL pages to: {filename}\n")







    # def search(
    #     self,
    #     keyword: str,
    #     intl_class: str = None,
    #     filing_status: str = None,
    #     max_pages: int = 5
    # ) -> List:

    #     results = []
    #     raw_storage = []

    #     gen = self.client.search_trademark(
    #         keyword=keyword,
    #         intl_class=intl_class,
    #         filing_status=filing_status,
    #         max_pages=max_pages
    #     )

    #     for item in gen:
    #         raw_storage.append(item)

    #         record = normalize_item(item)

    #         sim_score = score_similarity(keyword, record.mark_text or "")
    #         record.raw["similarity_score"] = sim_score

    #         results.append(record)

    #     # Save raw Atom output
    #     self._store_search_data(keyword, raw_storage)

    #     return results
    # def _store_search_data(self, keyword: str, data: list):

    #     BASE_DIR = Path(__file__).resolve().parent.parent.parent
    #     folder = BASE_DIR / "search_data"
    #     folder.mkdir(exist_ok=True)

    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     filename = folder / f"search_{keyword}_{timestamp}.json"

    #     with open(filename, "w", encoding="utf-8") as f:
    #         json.dump(data, f, indent=2, ensure_ascii=False)

    #     print(f"\n📁 Search data saved to: {filename}\n")












    # def _store_search_data(self, keyword: str, data: list):
    #     folder = "search_data"
    #     os.makedirs(folder, exist_ok=True)

    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     filename = f"{folder}/search_{keyword}_{timestamp}.json"

    #     with open(filename, "w", encoding="utf-8") as f:
    #         json.dump(data, f, indent=2, ensure_ascii=False)

    #     print(f"\n📁 Search data saved to: {filename}\n")

# from app.services.uspto_api_client import USPTOAPIClient


# class TrademarkSearchService:
#     def __init__(self):
#         self.client = USPTOAPIClient()

#     def search(self, search_input):
#         # --------- Input Validation ---------
#         if not search_input.keyword:
#             raise ValueError("Keyword is required")

#         if not search_input.intl_class:
#             raise ValueError("International class is required")

#         if not search_input.filing_status:
#             raise ValueError("Filing status is required")

#         # Normalize status
#         status = search_input.filing_status.strip().upper()

#         if status.startswith("L"):
#             status = "LIVE"
#         elif status.startswith("P"):
#             status = "PENDING"
#         else:
#             raise ValueError("Status must be LIVE or PENDING")

#         # --------- Call USPTO API ---------
#         raw_data = self.client.search_trademark(
#             keyword=search_input.keyword.strip(),
#             intl_class=search_input.intl_class,
#             filing_status=status
#         )

#         # --------- Format Response ---------
#         results = []

#         if "results" in raw_data:
#             for item in raw_data["results"]:
#                 results.append({
#                     "serial_number": item.get("serialNumber"),
#                     "registration_number": item.get("registrationNumber"),
#                     "mark_literal": item.get("markLiteral"),
#                     "status": item.get("applicationStatus"),
#                     "international_class": item.get("internationalClassCode"),
#                     "owner": item.get("ownerName")
#                 })

#         return results
# app/services/trademark_search_service.py
# from app.services.atom_api_client import AtomAPIClient, AtomAPIError
# from app.similarity.dupont_engine import score_similarity
# from app.services.response_parser import normalize_item
# from app.config import ATOM_API_KEY, ATOM_USER_ID

# from typing import List
# from app.models.trademark_record import TrademarkRecord
# import logging

# logger = logging.getLogger(__name__)


# class TrademarkSearchService:
#     def __init__(self):
#         self.client = AtomAPIClient()
#         # self.client = AtomAPIClient(
#         #     user_id=int(ATOM_USER_ID),
#         #     api_token=ATOM_API_KEY
#         # )
#     def search(
#         self,
#         keyword: str,
#         intl_class: str = None,
#         filing_status: str = None,
#         max_pages: int = 5
#     ) -> List[TrademarkRecord]:

#         results = []

#         gen = self.client.search_trademark(
#             keyword,
#             intl_class=intl_class,
#             filing_status=filing_status,
#             max_pages=max_pages
#         )

#         for item in gen:
#             rec = normalize_item(item)

#             # similarity scoring
#             sim_score = score_similarity(keyword, rec.mark_text or "")

#             # if sim_score >= 0.65:
#             rec.raw["similarity_score"] = sim_score
#             results.append(rec)

#         return results


#     # def search(self, keyword: str, intl_class: str = None, filing_status: str = None, max_pages: int = 5) -> List[TrademarkRecord]:
#     #     results = []
#     #     try:
#     #         gen = self.client.search_trademark(keyword, intl_class=intl_class, filing_status=filing_status, max_pages=max_pages)
#     #         for item in gen:
#     #             rec = normalize_item(item)
#     #             results.append(rec)
#     #     except AtomAPIError as e:
#     #         logger.error("Atom API error: %s", e)
#     #         raise
#     #     return results