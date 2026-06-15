"""
GST Due Date Calculator
References: Section from academic report and Mistral implementation details.
Dynamic due dates as of June 2026.
"""

import datetime
from datetime import date, timedelta

class GSTDueDateCalculator:
    def __init__(self):
        self.today = date.today()

    def get_gstr1_due_date(self, filing_type='monthly', ref_date=None):
        if ref_date is None:
            ref_date = self.today
        if filing_type == 'monthly':
            if ref_date.month == 12:
                return date(ref_date.year + 1, 1, 11)
            return date(ref_date.year, ref_date.month + 1, 11)
        elif filing_type == 'qrmp':
            # Simplified quarter logic for demo
            month = ref_date.month
            if month in [1,2,3]: q_end = 3
            elif month in [4,5,6]: q_end = 6
            elif month in [7,8,9]: q_end = 9
            else: q_end = 12
            if q_end == 12:
                return date(ref_date.year + 1, 1, 13)
            return date(ref_date.year, q_end + 1, 13)
        raise ValueError("Invalid filing type")

    def get_gstr3b_due_date(self, filing_type='monthly', state_group='A', ref_date=None):
        if ref_date is None:
            ref_date = self.today
        if filing_type == 'monthly':
            if ref_date.month == 12:
                return date(ref_date.year + 1, 1, 20)
            return date(ref_date.year, ref_date.month + 1, 20)
        elif filing_type == 'qrmp':
            month = ref_date.month
            if month in [1,2,3]: q_end = 3
            elif month in [4,5,6]: q_end = 6
            elif month in [7,8,9]: q_end = 9
            else: q_end = 12
            next_m = 1 if q_end == 12 else q_end + 1
            year = ref_date.year + 1 if q_end == 12 else ref_date.year
            day = 22 if state_group.upper() == 'A' else 24
            return date(year, next_m, day)
        raise ValueError("Invalid filing type")

    def calculate_late_fee(self, days_delayed, has_tax_liability=True):
        if days_delayed <= 0:
            return {"total_fee": 0, "cgst": 0, "sgst": 0}
        if has_tax_liability:
            daily = 50
            max_cap = 5000
        else:
            daily = 20
            max_cap = 2000
        total = min(days_delayed * daily, max_cap)
        return {
            "total_fee": total,
            "cgst": total // 2,
            "sgst": total // 2
        }