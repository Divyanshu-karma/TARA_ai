"""
extract_pairs.py

Utilities to extract (trademark_name, serial_number) pairs from JSON search files
stored under the project-level `search_data/` folder.

- Robust to missing keys and malformed records.
- Yields generator of tuples: (trademark_name, serial_number, source_filename, record_index)
- If serial_number missing, tries a regex fallback (searches for 7-9 digit numbers).
- Normalizes trademark_name by stripping whitespace.
- Optional deduplication by serial_number or trademark_name.
"""

from pathlib import Path
import json
import re
import logging
from typing import Iterator, Tuple, Optional, Set, Iterable

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Regex fallback for serial numbers (USPTO serials are commonly 7–8 digits; allow 6–9)
SERIAL_REGEX = re.compile(r"\b\d{6,9}\b")


def _get_value_case_insensitive(d: dict, keys: Iterable[str]):
    """Return first non-empty value for any key in `keys` (case-insensitive) from dict d."""
    lowered = {k.lower(): k for k in d.keys()}
    for key in keys:
        if key.lower() in lowered:
            val = d.get(lowered[key.lower()])
            if val not in (None, "", []):
                return val
    return None


def _search_for_serial_in_obj(obj) -> Optional[str]:
    """
    Recursively search object for a plausible serial number using SERIAL_REGEX.
    Returns the first match as string, or None.
    """
    if obj is None:
        return None
    if isinstance(obj, str):
        m = SERIAL_REGEX.search(obj)
        if m:
            return m.group(0)
        return None
    if isinstance(obj, (int, float)):
        s = str(obj)
        if SERIAL_REGEX.fullmatch(s):
            return s
        return None
    if isinstance(obj, dict):
        for v in obj.values():
            found = _search_for_serial_in_obj(v)
            if found:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = _search_for_serial_in_obj(v)
            if found:
                return found
    return None


def extract_pair_from_record(rec: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Given a single record (dict) from Atom JSON, extract (trademark_name, serial_number).
    Returns (name_or_None, serial_or_None).
    """
    # Common keys observed in Atom outputs
    name_keys = ["trademark_name", "mark_text", "name", "trademark", "title"]
    serial_keys = ["serial_number", "serial", "serialNo", "application_serial"]

    # Try direct lookup (case-insensitive)
    name = _get_value_case_insensitive(rec, name_keys)
    serial = _get_value_case_insensitive(rec, serial_keys)

    # If serial still missing, try nested 'raw' or any nested structure
    if serial is None:
        # direct nested fields
        if isinstance(rec.get("raw"), dict):
            serial = _get_value_case_insensitive(rec["raw"], serial_keys)
        # fallback: search entire object for numeric token
        if serial is None:
            serial = _search_for_serial_in_obj(rec)

    # Normalize name
    if isinstance(name, str):
        name = name.strip() or None
    # If name missing, try from raw dict
    if name is None and isinstance(rec.get("raw"), dict):
        name = _get_value_case_insensitive(rec["raw"], name_keys)
        if isinstance(name, str):
            name = name.strip() or None

    # If still missing, try to infer from other text fields (like description), but not reliable
    if name is None:
        # prefer shorter strings that look like a mark name
        candidates = []
        for k, v in rec.items():
            if isinstance(v, str) and 1 < len(v) < 200:
                candidates.append(v.strip())
        if candidates:
            # Heuristic: choose the shortest textual candidate (often a name)
            candidates.sort(key=len)
            name = candidates[0]

    return name, serial

def iterate_pairs_from_file(
    file_path: Path,
    dedupe_by: str | None = "serial"
):
    """
    Iterate through ONE JSON file and extract (trademark_name, serial_number).

    Yields:
        (trademark_name, serial_number, record_index)
    """

    seen_serials = set()
    seen_names = set()

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.exception("Failed to read JSON file %s: %s", file_path, e)
        return

    if not isinstance(data, list):
        logger.error("JSON file must contain a list of objects.")
        return

    for idx, rec in enumerate(data):

        if not isinstance(rec, dict):
            continue

        name, serial = extract_pair_from_record(rec)

        serial_key = serial.strip() if isinstance(serial, str) else None
        name_key = name.strip().lower() if isinstance(name, str) else None

        # optional deduplication
        if dedupe_by == "serial" and serial_key:
            if serial_key in seen_serials:
                continue
            seen_serials.add(serial_key)

        elif dedupe_by == "name" and name_key:
            if name_key in seen_names:
                continue
            seen_names.add(name_key)

        yield name, serial, idx
# def iterate_pairs_from_folder(
#     folder: Path,
#     pattern: str = "search_*.json",
#     dedupe_by: Optional[str] = "serial",  # "serial" | "name" | None
# ) -> Iterator[Tuple[Optional[str], Optional[str], Path, int]]:
#     """
#     Iterate through JSON files in folder (non-recursive) matching pattern and yield pairs.

#     Yields tuples: (trademark_name or None, serial_number or None, source_filepath, record_index).

#     dedupe_by:
#       - "serial": skip records with duplicate serial numbers
#       - "name": skip duplicate trademark_name (case-insensitive)
#       - None: no deduplication
#     """
#     folder = Path(folder)
#     if not folder.exists():
#         logger.error("search_data folder does not exist: %s", folder)
#         return

#     seen_serials: Set[str] = set()
#     seen_names: Set[str] = set()

#     files = sorted(folder.glob(pattern))
#     for fp in files:
#         try:
#             data = json.loads(fp.read_text(encoding="utf-8"))
#         except Exception as e:
#             logger.exception("Failed to read/parse %s: %s", fp, e)
#             continue

#         if not isinstance(data, list):
#             logger.warning("Expected a JSON array in %s but got %s; attempting to recover", fp, type(data))
#             # if file contains single object, wrap it
#             if isinstance(data, dict):
#                 data = [data]
#             else:
#                 continue

#         for idx, rec in enumerate(data):
#             if not isinstance(rec, dict):
#                 # skip unexpected types
#                 continue

#             name, serial = extract_pair_from_record(rec)

#             # Normalize serial/name for dedupe comparisons
#             serial_key = serial.strip() if isinstance(serial, str) else None
#             name_key = name.strip().lower() if isinstance(name, str) else None

#             if dedupe_by == "serial" and serial_key:
#                 if serial_key in seen_serials:
#                     continue
#                 seen_serials.add(serial_key)
#             elif dedupe_by == "name" and name_key:
#                 if name_key in seen_names:
#                     continue
#                 seen_names.add(name_key)

#             yield name, serial, fp, idx


# Convenience helper to return list (if you prefer list)
# def collect_pairs_from_folder(folder: Path, pattern: str = "search_*.json", dedupe_by: Optional[str] = "serial"):
#     return list(iterate_pairs_from_folder(folder=folder, pattern=pattern, dedupe_by=dedupe_by))


# Small helper to iterate and call function on each mark name
# def process_each_mark_name(folder: Path, callback, pattern: str = "search_*.json", dedupe_by: Optional[str] = "serial"):
#     """
#     callback: callable that accepts (trademark_name, serial_number, source_filepath, record_index)
#     """
#     for name, serial, fp, idx in iterate_pairs_from_folder(folder=folder, pattern=pattern, dedupe_by=dedupe_by):
#         try:
#             callback(name, serial, fp, idx)
#         except Exception:
#             logger.exception("Callback failed for %s (serial=%s) from %s[%d]", name, serial, fp, idx)