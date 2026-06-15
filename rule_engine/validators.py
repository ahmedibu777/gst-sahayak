"""
Input Validators: GSTIN, HSN, Dates
"""

import re
from datetime import datetime

def validate_gstin(gstin: str) -> bool:
    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    return bool(re.match(pattern, gstin.upper()))

def validate_hsn(hsn: str) -> bool:
    return len(hsn) >= 4 and hsn.isdigit()

def validate_date(date_str: str, fmt="%d-%m-%Y") -> bool:
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False

def is_future_date(date_str: str) -> bool:
    try:
        d = datetime.strptime(date_str, "%d-%m-%Y").date()
        return d > datetime.now().date()
    except:
        return False