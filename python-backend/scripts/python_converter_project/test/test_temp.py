import pytest
from converters.temp import convert_temp

@pytest.mark.parametrize(
    "value, from_u, to_u, expected",
    [
        (0,   "C", "F", 32),
        (100, "C", "F", 212),
        (32,  "F", "C", 0),
        (212, "F", "C", 100),
        (0,   "C", "K", 273.15),
        (273.15, "K", "C", 0),
        (-40, "C", "F", -40),   
        (-40, "F", "C", -40),
    ],
)
def test_temp_basic_conversions(value, from_u, to_u, expected):
    assert convert_temp(value, from_u, to_u) == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize("value, unit", [(0, "C"), (32, "F"), (273.15, "K"), (-40, "C")])
def test_temp_identity(value, unit):
    assert convert_temp(value, unit, unit) == value


@pytest.mark.parametrize(
    "value, unit_a, unit_b",
    [
        (25.3, "C", "F"),
        (310.15, "K", "C"),
        (77.77, "F", "K"),
        (-40, "C", "F"),
    ],
)
def test_temp_round_trip(value, unit_a, unit_b):
    mid = convert_temp(value, unit_a, unit_b)
    back = convert_temp(mid, unit_b, unit_a)
    assert back == pytest.approx(value, abs=1e-9)


def test_temp_absolute_zero_exact_allowed():
    assert convert_temp(-273.15, "C", "K") == pytest.approx(0.0, abs=1e-12)
    assert convert_temp(0.0, "K", "C") == pytest.approx(-273.15, abs=1e-12)
    assert convert_temp(-459.67, "F", "K") == pytest.approx(0.0, abs=1e-10)

def test_temp_below_absolute_zero_raises_for_input_scale():
    with pytest.raises(ValueError, match="Temperature out of range physically possible"):
        convert_temp(-273.151, "C", "K")
    with pytest.raises(ValueError, match="Temperature out of range physically possible"):
        convert_temp(-1e-12, "K", "C")
    with pytest.raises(ValueError, match="Temperature out of range physically possible"):
        convert_temp(-459.671, "F", "C")


@pytest.mark.parametrize(
    "value, from_u, to_u",
    [
        (0, "X", "C"),
        (0, "C", "Y"),
        (0, "X", "Y"),
    ],
)
def test_temp_invalid_units_raise(value, from_u, to_u):
    with pytest.raises(ValueError, match="Unit not supported"):
        convert_temp(value, from_u, to_u)

