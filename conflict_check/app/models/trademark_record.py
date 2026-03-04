# app/models/trademark_record.py

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class TrademarkRecord:
    mark_text: Optional[str]
    intl_class: Optional[str]
    filing_status: Optional[str]
    serial_number: Optional[str]
    owner: Optional[str]
    description: Optional[str]
    raw: Dict[str, Any]