
# interactive.py
"""
Interactive mode for the converter .
Reuses normalize() from cli.py and the same converter functions.
"""

from pathlib import Path
import json

# Reuse your existing pieces
from cli import normalize   # uses the same aliases.json and rules
from converters.units import convert_mass, convert_volume, convert_length
from converters.temp import convert_temp
from converters.currency import convert_currency

# Load aliases to show supported options to the user
_JSON_PATH = Path(__file__).resolve().parent / "data" / "aliases.json"
with open(_JSON_PATH, "r", encoding="utf-8") as f:
    ALIASES = json.load(f)  # shape: { mode: { standard: [aliases...] } }

MODES = {
    "mass": {
        "fn": convert_mass,
        "labels": ("amount", "from unit", "to unit"),
        "note": "Examples: kg, g, lb, oz",
    },
    "volume": {
        "fn": convert_volume,
        "labels": ("amount", "from unit", "to unit"),
        "note": "Examples: L, mL, gal, fl oz",
    },
    "length": {
        "fn": convert_length,
        "labels": ("amount", "from unit", "to unit"),
        "note": "Examples: m, km, cm, mi, ft, in",
    },
    "temp": {
        "fn": convert_temp,
        "labels": ("value", "from unit", "to unit"),
        "note": "Use C, F, K",
    },
    "currency": {
        "fn": convert_currency,
        "labels": ("amount", "from currency", "to currency"),
        "note": "Examples: USD, EUR, MXN, COP",
    },
}

HELP_TEXT = """
Commands:
  help                Show this help
  modes               List available modes
  units <mode>        Show canonical units & aliases for a mode (e.g., 'units length')
  quit / exit         Leave interactive mode

Convert:
  1) Choose mode when prompted (mass | volume | length | temp | currency)
  2) Enter value, from, to
     You can type aliases (e.g., 'meters', 'pies', '$', 'dólar') — they get normalized.

Examples:
  mode: length  | value: 12.5 | from: km   | to: m
  mode: temp    | value: 32   | from: F    | to: C
  mode: currency| value: 50   | from: EUR  | to: MXN
"""

def list_modes():
    print("\nAvailable modes:")
    for m, cfg in MODES.items():
        print(f"  - {m:8s}  {cfg['note']}")
    print()

def list_units(mode: str):
    mode = mode.strip().lower()
    if mode not in ALIASES:
        print(f"Unknown mode: {mode}")
        return
    print(f"\nUnits & aliases for '{mode}':")
    data = ALIASES[mode]
    # Expecting: { standard: [aliases...] }
    for standard, aliases in data.items():
        # ensure aliases is a list; some JSONs might store a single string by mistake
        if isinstance(aliases, str):
            aliases = [aliases]
        alias_list = ", ".join(sorted(set(aliases)))
        print(f"  {standard}: {alias_list}")
    print()

def ask(prompt: str) -> str:
    return input(prompt).strip()

def parse_float(s: str) -> float:
    # Accept commas or spaces in numbers (e.g., "1 234,56")
    s = s.replace(" ", "").replace(",", ".")
    return float(s)

def main():
    print("=== Converter Interactive Mode ===")
    print("Type 'help' to see commands.\n")

    while True:
        raw = ask("cmd> ").lower()

        if raw in ("quit", "exit"):
            print("Bye!")
            return
        if raw == "help" or raw == "?":
            print(HELP_TEXT)
            continue
        if raw == "modes":
            list_modes()
            continue
        if raw.startswith("units"):
            parts = raw.split()
            if len(parts) == 2:
                list_units(parts[1])
            else:
                print("Usage: units <mode>")
            continue
        if raw == "":
            continue

        # Otherwise, treat this as the chosen mode
        mode = raw
        if mode not in MODES:
            print(f"Unknown command or mode: {mode}. Type 'modes' to see options.")
            continue

        fn = MODES[mode]["fn"]
        label_amount, label_from, label_to = MODES[mode]["labels"]

        try:
            value_str = ask(f"Enter {label_amount}: ")
            value = parse_float(value_str)

            from_u = ask(f"Enter {label_from}: ")
            to_u = ask(f"Enter {label_to}: ")

            # Normalize symbols/codes using your existing normalize()
            from_std = normalize(from_u, mode)
            to_std = normalize(to_u, mode)

            # Perform conversion
            result = fn(value, from_std, to_std)
            # Round nicely for display; keep raw precision in your CLI if needed
            print(f"Result: {round(result, 6)}\n")

        except ValueError as ve:
            print(f"Error: {ve}\n")
        except Exception as ex:
            print(f"Unexpected error: {ex}\n")

if __name__ == "__main__":
    main()

