import pytest
from rule_engine.due_dates import GSTDueDateCalculator
from datetime import date

def test_gstr3b_monthly():
    calc = GSTDueDateCalculator()
    # Test for a known date
    d = calc.get_gstr3b_due_date('monthly', ref_date=date(2026, 4, 1))
    assert d == date(2026, 5, 20)

def test_late_fee():
    calc = GSTDueDateCalculator()
    result = calc.calculate_late_fee(5, True)
    assert result['total_fee'] == 250