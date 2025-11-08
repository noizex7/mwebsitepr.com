import pytest
import converters.currency as currency


@pytest.fixture(autouse=True)
def mock_usd_base(monkeypatch):
    mock_rates = {
        "USD": 1.0,
        "EUR": 0.9,
        "GBP": 0.8,
        "JPY": 150.0,
        "ARS": 900.0,
    }
    monkeypatch.setattr(currency, "USD_BASE", mock_rates)
    yield


def approx(a, b, eps=1e-9):
    return abs(a - b) < eps


def test_usd_to_eur():
    result = currency.convert_currency(100, "USD", "EUR")
    assert approx(result, 90)

def test_eur_to_usd():
    result = currency.convert_currency(90, "EUR", "USD")
    assert approx(result, 100)

def test_usd_to_gbp():
    result = currency.convert_currency(100, "USD", "GBP")
    assert approx(result, 80)

def test_gbp_to_usd():
    result = currency.convert_currency(80, "GBP", "USD")
    assert approx(result, 100)

def test_usd_to_jpy():
    result = currency.convert_currency(1, "USD", "JPY")
    assert approx(result, 150)

def test_jpy_to_usd():
    result = currency.convert_currency(150, "JPY", "USD")
    assert approx(result, 1)


def test_eur_to_gbp():
    result = currency.convert_currency(90, "EUR", "GBP")
    assert approx(result, 80)

def test_ars_to_jpy():
    result = currency.convert_currency(900, "ARS", "JPY")
    assert approx(result, 150)


def test_identity_conversion():
    assert currency.convert_currency(123, "USD", "USD") == 123

def test_zero_amount():
    assert currency.convert_currency(0, "USD", "EUR") == 0

def test_negative_amount():
    result = currency.convert_currency(-100, "USD", "EUR")
    assert approx(result, -90)


def test_invalid_currency_from():
    with pytest.raises(ValueError, match="Currency not supported"):
        currency.convert_currency(1, "XXX", "USD")

def test_invalid_currency_to():
    with pytest.raises(ValueError, match="Currency not supported"):
        currency.convert_currency(1, "USD", "ZZZ")

