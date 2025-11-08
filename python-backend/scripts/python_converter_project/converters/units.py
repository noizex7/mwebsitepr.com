# converters/units.py
from __future__ import  annotations
from pathlib import Path
import json
from typing import Dict, Mapping

# Path to this file -> parent (converters) -> parent (project root) -> data/units.json
_JSON_PATH = Path(__file__).resolve().parents[1] / "data" / "units.json"

with open(_JSON_PATH, "r") as f:
    _FACTORS: Dict[str, Dict[str, float]] = json.load(f)

_ERROR_MESSAGE = "Unit not supported"


def _convert(value: float, from_u: str, to_u: str, factors: Mapping[str, float]) -> float:
    if from_u not in factors or to_u not in factors:
        available = ", ".join(sorted(factors.keys()))
        raise ValueError(f"{_ERROR_MESSAGE}. Available: {available}")
    base = value * factors[from_u]         
    return base / factors[to_u]            

def convert_length(value: float, from_u: str, to_u: str) -> float:
    return _convert(value,from_u, to_u, _FACTORS["length"])   

def convert_volume(value: float, from_u: str, to_u: str) -> float:
    return _convert(value,from_u, to_u, _FACTORS["volume"])

def convert_mass(value: float, from_u: str, to_u: str) -> float:
    return _convert(value,from_u, to_u, _FACTORS["mass"])

def convert(category: str, value: float, from_u: str, to_u: str) -> float:
    cat = category.lower()
    if cat not in _FACTORS:
        raise ValueError(f"Category not supported. Available: {', '.join(sorted(_FACTORS))}")
    return _convert(value, from_u, to_u, _FACTORS[cat])



