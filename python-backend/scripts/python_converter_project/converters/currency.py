# converters/currency.py
"""Currency converter backed by Frankfurter.dev with graceful fallbacks."""

from __future__ import annotations

from typing import Dict

import requests

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


def _fetch_rates() -> Dict[str, float]:
    try:
        resp = requests.get(FRANKFURTER_URL, params={"base": "USD"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", {})
    except requests.RequestException as exc:  # pragma: no cover - live HTTP call
        print(
            "Warning: could not fetch live FX rates from Frankfurter.dev:", exc,
            flush=True,
        )
        rates = {}

    rates["USD"] = 1.0
    return rates


USD_BASE = _fetch_rates()


def convert_currency(amount: float, from_ccy: str, to_ccy: str) -> float:
    r = USD_BASE
    if from_ccy not in r or to_ccy not in r:
        if len(r) == 1:
            raise RuntimeError(
                "Currency rates are unavailable right now. "
                "Check your network connection and try again."
            )
        raise ValueError("Currency not supported")

    usd = amount / r[from_ccy]
    return usd * r[to_ccy]
