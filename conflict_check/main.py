# main.py

from pathlib import Path
import json
from datetime import datetime

from app.controllers.search_controller import handle_search
from app.utils.extract_pairs import iterate_pairs_from_file
from app.similarity.factor1 import score_factor1


def main():

    keyword = input("mark_text: ").strip()
    intl_class = input("class : ").strip() or None
    filing_status = input("status (active/pending/dead/all): ").strip() or None

    # ---------------------------------------------------
    # STEP 1 — Fetch trademarks from Atom API
    # ---------------------------------------------------
    results = handle_search(keyword, intl_class, filing_status)

    out = [r.__dict__ for r in results]
    print(json.dumps(out, indent=2, ensure_ascii=False))

    # ---------------------------------------------------
    # STEP 2 — Find newest JSON search file
    # ---------------------------------------------------
    BASE_DIR = Path(__file__).resolve().parent
    search_folder = BASE_DIR / "search_data"

    json_files = sorted(
        search_folder.glob("search_*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not json_files:
        print("No JSON files found in search_data")
        return

    latest_file = json_files[0]

    print("\nUsing JSON file:", latest_file)

    # ---------------------------------------------------
    # STEP 3 — Run Factor-1 Similarity
    # ---------------------------------------------------
    applied_mark = keyword
    analysis_results = []

    print("\nRunning DuPont Factor-1 similarity analysis...\n")

    for name, serial, idx in iterate_pairs_from_file(latest_file):

        if not name:
            continue

        conflicting_mark = name
        score = score_factor1(applied_mark, conflicting_mark)

        record = {
            "applied_mark": applied_mark,
            "conflicting_mark": conflicting_mark,
            "serial": serial,
            "composite_score": score.composite_score
        }

        analysis_results.append(record)

    # ---------------------------------------------------
    # STEP 4 — Sort by risk level
    # ---------------------------------------------------
    ranked_results = sorted(
        analysis_results,
        key=lambda x: x["composite_score"],
        reverse=True
    )

    print("\nTOP 10 HIGHEST RISK CONFLICTS\n")

    for r in ranked_results[:10]:

        print("Applied Mark:", r["applied_mark"])
        print("Conflicting Mark:", r["conflicting_mark"])
        print("Serial:", r["serial"])
        print("Composite Score:", r["composite_score"])
        print("--------------------------")

    # ---------------------------------------------------
    # STEP 5 — Save full analysis to JSON
    # ---------------------------------------------------
    output_folder = BASE_DIR / "analysis_output"
    output_folder.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = output_folder / f"factor1_{keyword.replace(' ','_')}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ranked_results, f, indent=2, ensure_ascii=False)

    print(f"\nFull analysis saved to:\n{filename}\n")


if __name__ == "__main__":
    main()






# # main.py

# from pathlib import Path
# import json

# from app.controllers.search_controller import handle_search
# from app.utils.extract_pairs import iterate_pairs_from_file
# from app.similarity.factor1 import score_factor1


# def main():

#     keyword = input("mark_text: ").strip()
#     intl_class = input("class : ").strip() or None
#     filing_status = input("status (active/pending/dead/all): ").strip() or None

#     # ---------------------------------------------------
#     # STEP 1: Fetch trademarks from Atom API
#     # ---------------------------------------------------
#     results = handle_search(keyword, intl_class, filing_status)

#     # print results returned by service (debug / inspection)
#     out = [r.__dict__ for r in results]
#     print(json.dumps(out, indent=2, ensure_ascii=False))

#     # ---------------------------------------------------
#     # STEP 2: Locate newest JSON file in search_data
#     # ---------------------------------------------------
#     BASE_DIR = Path(__file__).resolve().parent
#     search_folder = BASE_DIR / "search_data"

#     json_files = sorted(
#         search_folder.glob("search_*.json"),
#         key=lambda f: f.stat().st_mtime,
#         reverse=True
#     )

#     if not json_files:
#         print("No JSON files found in search_data")
#         return

#     latest_file = json_files[0]

#     print("\nUsing JSON file:", latest_file)

#     # ---------------------------------------------------
#     # STEP 3: Run DuPont Factor-1 Similarity
#     # ---------------------------------------------------
#     applied_mark = keyword

#     print("\nRunning DuPont Factor-1 Similarity Analysis...\n")

#     for name, serial, idx in iterate_pairs_from_file(latest_file):

#         if not name:
#             continue

#         conflicting_mark = name

#         score = score_factor1(applied_mark, conflicting_mark)

#         print("Applied Mark:", applied_mark)
#         print("Conflicting Mark:", conflicting_mark)
#         print("Serial:", serial)
#         print("Composite Score:", score.composite_score)
#         print("--------------------------")


# if __name__ == "__main__":
#     main()








# # main.py
# from app.utils.extract_pairs import iterate_pairs_from_file
# from app.similarity.factor1 import score_factor1
# from pathlib import Path
# from app.controllers.search_controller import handle_search
# from app.utils.extract_pairs import iterate_pairs_from_file
# import json


# def main():

#     keyword = input("mark_text: ").strip()
#     intl_class = input("class : ").strip() or None
#     filing_status = input("status (active/pending/dead/all): ").strip() or None

#     # ---------------------------------------------------
#     # STEP 1: Fetch trademarks from Atom API
#     # ---------------------------------------------------
#     results = handle_search(keyword, intl_class, filing_status)

#     # print results returned by service
#     out = [r.__dict__ for r in results]
#     print(json.dumps(out, indent=2, ensure_ascii=False))

#     # ---------------------------------------------------
#     # STEP 2: Find latest JSON file saved in search_data
#     # ---------------------------------------------------
#     # search_folder = Path("search_data")
#     BASE_DIR = Path(__file__).resolve().parent
#     search_folder = BASE_DIR / "search_data"

#     json_files = sorted(
#         search_folder.glob("search_*.json"),
#         key=lambda f: f.stat().st_mtime,
#         reverse=True
#     )

#     if not json_files:
#         print("No JSON files found in search_data")
#         return

#     latest_file = json_files[0]

#     print("\nUsing JSON file:", latest_file)

#     # ---------------------------------------------------
#     # STEP 3: Extract (trademark_name, serial_number)
#     # ---------------------------------------------------
#     print("\nExtracted pairs:\n")

#     for name, serial, idx in iterate_pairs_from_file(latest_file):

#         print("Index:", idx)
#         print("Trademark:", name)
#         print("Serial:", serial)
#         print("----------------------")

#         # Goal1: send trademark_name to other functions
#         if name:
#             pass
#             # example:
#             # some_function(name)


# if __name__ == "__main__":
#     main()






















# # main.py
# from app.controllers.search_controller import handle_search
# from app.services.trademark_search_service import TrademarkSearchService
# import json

# def main():
#     keyword = input("mark_text: ").strip()
#     intl_class = input("class : ").strip() or None
#     filing_status = input("status (active/pending/dead/all): ").strip() or None

#     results = handle_search(keyword, intl_class, filing_status)
#     # print a compact JSON-ish list
#     out = [r.__dict__ for r in results]
#     print(json.dumps(out, indent=2, ensure_ascii=False))
#     print(dir(TrademarkSearchService))
# if __name__ == "__main__":
#     main()