import pytest
from converters.units import convert_length

def approx(a, b, eps=1e-9):
    return abs(a - b) < eps


def test_length_m_to_km():
    assert convert_length(1000, "m", "km") == 1.0

def test_length_km_to_m():
    assert convert_length(1, "km", "m") == 1000.0

def test_length_m_to_cm():
    assert convert_length(2, "m", "cm") == 200.0

def test_length_cm_to_m():
    assert convert_length(250, "cm", "m") == 2.5

def test_length_m_to_mm():
    assert convert_length(1.5, "m", "mm") == 1500.0

def test_length_mm_to_m():
    assert convert_length(3000, "mm", "m") == 3.0

def test_length_m_to_ft():
    assert convert_length(1, "m", "ft") == pytest.approx(3.28084, rel=1e-5)

def test_length_ft_to_m():
    assert convert_length(3.28084, "ft", "m") == pytest.approx(1.0, rel=1e-5)

def test_length_m_to_in():
    assert convert_length(1, "m", "in") == pytest.approx(39.3701, rel=1e-5)

def test_length_in_to_m():
    assert convert_length(39.3701, "in", "m") == pytest.approx(1.0, rel=1e-5)

def test_length_mi_to_km():
    assert convert_length(1, "mi", "km") == pytest.approx(1.609344, rel=1e-6)

def test_length_km_to_mi():
    assert convert_length(1.609344, "km", "mi") == pytest.approx(1.0, rel=1e-6)


def test_length_identity():
    assert convert_length(42, "m", "m") == 42

def test_length_round_trip():
    x = 123.456
    result = convert_length(convert_length(x, "m", "ft"), "ft", "m")
    assert pytest.approx(result, rel=1e-9) == x


def test_length_zero():
    assert convert_length(0, "km", "m") == 0

def test_length_negative():
    assert convert_length(-2, "km", "m") == -2000


def test_length_invalid_from():
    with pytest.raises(ValueError, match="Unit not supported"):
        convert_length(1, "yard", "m")

def test_length_invalid_to():
    with pytest.raises(ValueError, match="Unit not supported"):
        convert_length(1, "m", "yard")

