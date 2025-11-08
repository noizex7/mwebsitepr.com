from converters.units import convert_mass

def approx(a, b, eps=1e-9): 
    return abs(a - b) < eps

def test_mass_g_to_kg():
    assert convert_mass(1000, "g", "kg") == 1.0

def test_mass_kg_to_g():
    assert convert_mass(1, "kg", "g") == 1000.0

def test_mass_t_to_kg():
    assert convert_mass(1, "t", "kg") == 1000.0

def test_mass_kg_to_t():
    assert convert_mass(2500, "kg", "t") == 2.5

def test_mass_mg_to_g():
    assert convert_mass(5000, "mg", "g") == 5.0

def test_mass_dag_to_g():
    assert convert_mass(3, "dag", "g") == 30.0

def test_mass_hg_to_kg():
    assert convert_mass(12, "hg", "kg") == 1.2

def test_mass_dg_to_g():
    assert approx(convert_mass(7, "dg", "g"), 0.7)

def test_mass_cg_to_g():
    assert convert_mass(25, "cg", "g") == 0.25

def test_mass_identity_unit():
    assert convert_mass(42, "g", "g") == 42

def test_mass_round_trip_g_to_kg_to_g():
    x = 12345.6
    assert approx(convert_mass(convert_mass(x, "g", "kg"), "kg", "g"), x)

def test_mass_zero():
    assert convert_mass(0, "kg", "g") == 0

def test_mass_negative():
    assert convert_mass(-2, "kg", "g") == -2000.0

def test_mass_invalid_from():
    try:
        convert_mass(1, "lb", "kg")
    except ValueError as e:
        assert "Unit not supported" in str(e)
    else:
        assert False, "Expected ValueError for unsupported unit (from)"

def test_mass_invalid_to():
    try:
        convert_mass(1, "kg", "lb")
    except ValueError as e:
        assert "Unit not supported" in str(e)
    else:
        assert False, "Expected ValueError for unsupported unit (to)"

