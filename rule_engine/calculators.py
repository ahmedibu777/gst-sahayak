"""
Calculators for Late Fee, TDS (Section 194J), etc.
Production-grade with error handling.
"""

from .due_dates import GSTDueDateCalculator

def calculate_late_fee(days_delayed: int, has_liability: bool = True):
    calc = GSTDueDateCalculator()
    return calc.calculate_late_fee(days_delayed, has_liability)

def calculate_tds_194j(amount: float, service_type: str = "professional", has_pan: bool = True):
    threshold = 50000
    if amount <= threshold:
        return 0.0
    if not has_pan:
        rate = 20
    elif service_type == "professional":
        rate = 10
    else:
        rate = 2
    return round(amount * (rate / 100), 2)

def itc_eligibility_checker(supplier_registered: bool, in_gstr2b: bool, blocked: bool, received: bool):
    if not supplier_registered:
        return "Ineligible: Supplier not registered"
    if not in_gstr2b:
        return "Ineligible: Not in GSTR-2B. Contact supplier."
    if blocked:
        return "Blocked: Reverse in GSTR-3B Table 4(B)(1)"
    if not received:
        return "Ineligible: Goods not received"
    return "Eligible: Claim in GSTR-3B Table 4(A)"