from rule_engine.calculators import calculate_tds_194j, itc_eligibility_checker

def test_tds_below_threshold():
    assert calculate_tds_194j(40000, "professional", True) == 0.0

def test_tds_above():
    assert calculate_tds_194j(60000, "professional", True) == 6000.0

def test_itc_eligible():
    assert "Eligible" in itc_eligibility_checker(True, True, False, True)