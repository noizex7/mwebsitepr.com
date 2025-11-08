from converters.units import convert_volume
def test_volume_l_to_ml():
    assert convert_volume(1, "L", "mL") == 1000.0

def test_volume_ml_to_l():
    assert convert_volume(500, "mL", "L") == 0.5

def test_volume_m3_to_l():
    assert convert_volume(1, "m3", "L") == 1000.0

def test_volume_l_to_m3():
    assert convert_volume(1000, "L", "m3") == 1.0

def test_volume_dm3_to_l():
    assert convert_volume(1, "dm3", "L") == 1.0

def test_volume_cm3_to_mL():
    assert convert_volume(10, "cm3", "mL") == 10.0

def test_volume_invalid_unit_from():
    try:
        convert_volume(1, "gal", "L")
    except ValueError as e:
        assert "Unit not supported" in str(e)
    else:
        assert False, "Expected ValueError for unsupported unit"

def test_volume_invalid_unit_to():
    try:
        convert_volume(1, "L", "oz")
    except ValueError as e:
        assert "Unit not supported" in str(e)
    else:
        assert False, "Expected ValueError for unsupported unit"
