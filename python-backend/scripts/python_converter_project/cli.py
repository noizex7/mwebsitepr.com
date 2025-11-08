# cli.py
import argparse
from converters.currency import convert_currency
from converters.units import convert_mass, convert_volume, convert_length 
from converters.temp import convert_temp
from pathlib import Path
from typing import Dict, List
import json


# Path to this file -> parent (converters) -> parent (project root) -> data/units.json
_JSON_PATH = Path(__file__).resolve().parents[0] / "data" / "aliases.json"


with open(_JSON_PATH, "r") as f:
    aliases: Dict[str, Dict[str, List[str]]] = json.load(f)

def normalize(symbol: str, mode: str) -> str:
    s = symbol.strip().lower()

    for standard, forms in aliases[mode].items():
        if s in forms:
            return standard

    raise ValueError(f"Unidad desconocida: {symbol}")

def main():
    parser = argparse.ArgumentParser(description = "Converter")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_mass = sub.add_parser("mass")
    p_mass.add_argument("value", type=float)
    p_mass.add_argument("from_u")
    p_mass.add_argument("to_u")

    p_vol = sub.add_parser("volume")
    p_vol.add_argument("value", type=float)
    p_vol.add_argument("from_u")
    p_vol.add_argument("to_u")

    p_len = sub.add_parser("length")
    p_len.add_argument("value", type=float)
    p_len.add_argument("from_u")
    p_len.add_argument("to_u")

    p_temp = sub.add_parser("temp")
    p_temp.add_argument("value", type=float)
    p_temp.add_argument("from_u")
    p_temp.add_argument("to_u")

    p_fx = sub.add_parser("currency")
    p_fx.add_argument("amount", type=float)
    p_fx.add_argument("from_ccy")
    p_fx.add_argument("to_ccy")

    args = parser.parse_args()

    response = 0.0
    if args.mode == "mass":
        response = convert_mass(args.value, normalize(args.from_u, args.mode), normalize(args.to_u, args.mode))
    elif args.mode == "volume":
        response = convert_volume(args.value, normalize(args.from_u, args.mode), normalize(args.to_u, args.mode))
    elif args.mode == "length":
        response = convert_length(args.value, normalize(args.from_u, args.mode), normalize(args.to_u, args.mode))
    elif args.mode == "temp":
        response = convert_temp(args.value, normalize(args.from_u, args.mode), normalize(args.to_u, args.mode))
    elif args.mode == "currency":
        response = convert_currency(args.amount, normalize(args.from_ccy, args.mode), normalize(args.to_ccy, args.mode))
    print(round(response,2))

if __name__ == "__main__":
    main()
    #print(normalize("feet","length"))
