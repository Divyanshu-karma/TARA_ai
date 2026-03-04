# app/services/response_parser.py

from app.models.trademark_record import TrademarkRecord


def normalize_item(item: dict) -> TrademarkRecord:
    """
    Convert Atom API schema into internal TrademarkRecord model.
    """

    mark_text = item.get("trademark_name") or item.get("mark_text") or item.get("trademark") 
    intl_class = item.get("international_classes") or item.get("class")
    filing_status = item.get("status_category") or  item.get("filing_status") or item.get("status")
    serial_number = item.get("serial_number") or item.get("serialNo") or item.get("serial")
    owner = item.get("owners") or item.get("applicant") or item.get("owner_name")
    description = item.get("description")

    return TrademarkRecord(
        mark_text=mark_text,
        intl_class=intl_class,
        filing_status=filing_status,
        serial_number=serial_number,
        owner=owner,
        description=description,
        raw=item
    )


# app/services/response_parser.py
# from typing import Dict, Any
# from app.models.trademark_record import TrademarkRecord

# def normalize_item(item: Dict[str, Any]) -> TrademarkRecord:
#     # defensive mapping: check common keys
#     mark_text = item.get("mark_text") or item.get("name") or item.get("trademark") or item.get("mark") or item.get("trademark_name")
#     intl_class = item.get("class") or item.get("international_classes") or item.get("nice_class")
#     filing_status = item.get("filing_status") or item.get("status")
#     serial_number = item.get("serial_number") or item.get("serialNo") or item.get("serial")
#     owner = item.get("owner") or item.get("applicant") or item.get("owner_name")

#     return TrademarkRecord(
#         mark_text=mark_text,
#         intl_class=str(intl_class) if intl_class is not None else None,
#         filing_status=filing_status,
#         serial_number=serial_number,
#         owner=owner,
#         raw=item
#     )