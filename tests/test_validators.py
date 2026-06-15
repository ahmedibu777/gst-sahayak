from rule_engine.validators import validate_gstin, validate_hsn

def test_valid_gstin():
    assert validate_gstin("29ABCDE1234F1Z5") == True  # Correct 15-character GSTIN format

def test_invalid_gstin():
    assert validate_gstin("ABC123") == False

def test_hsn():
    assert validate_hsn("8517") == True