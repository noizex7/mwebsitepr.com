# Conversor

Conversor is a small Python toolkit that groups together the different converters that live under `cli.py` and `interactive.py`. It can convert between length, volume, mass, temperature, and currency values while accepting multiple aliases (Spanish and English) for every unit or currency.

## Features
- Five conversion modes (`mass`, `volume`, `length`, `temp`, `currency`) driven by the same validation and normalization helpers.
- Canonical units plus flexible aliases defined in `data/aliases.json`, so inputs such as `pies`, `meters`, or `$` all resolve to their standard symbols.
- Deterministic unit conversions backed by factors in `data/units.json` and temperature guardrails that reject impossible values.
- Live FX rates sourced from the [Frankfurter.dev](https://www.frankfurter.app/) API the first time `converters/currency.py` is imported.
- A scripted CLI (`cli.py`) and an interactive shell (`interactive.py`) that reuse the same converter functions.
- Pytest-based regression tests for each converter module.

## Requirements
- Python 3.10 or newer.
- Dependencies: `requests` (runtime) and `pytest` (tests). Install them with:

```bash
python -m pip install --upgrade pip
pip install requests pytest
```

## Project layout
```
conversor/
├── cli.py              # Argument-parsed command line front end
├── interactive.py      # REPL-like interface that reuses the same converters
├── converters/
│   ├── currency.py     # Uses Frankfurter.dev to build a USD-based rate table
│   ├── temp.py         # Temperature conversions with physical guardrails
│   └── units.py        # Length, mass, and volume conversions via factors
├── data/
│   ├── aliases.json    # Canonical symbols and all accepted aliases
│   └── units.json      # Conversion factors per mode
└── test/               # Pytest suites covering each converter
```

## Usage
### CLI mode
The CLI groups each converter under a subcommand. General shape:

```bash
python cli.py <mode> <value> <from_unit> <to_unit>
```

Examples:

```bash
python cli.py length 12.5 km m
python cli.py mass 10 kg g
python cli.py volume 2 L mL
python cli.py temp 68 F C
python cli.py currency 50 eur mxn
```

Every string you pass is normalized via `normalize()` and the alias table, so you can mix accents or language-specific names (`pies`, `dolares`, `meters`, etc.). All numeric results are printed rounded to two decimals.

### Interactive mode
If you prefer a guided flow, run:

```bash
python interactive.py
```

The REPL lets you list modes (`modes`), inspect aliases per mode (`units length`), or repeatedly run conversions without re-invoking the script.

## Currency conversions
`converters/currency.py` fetches rates from Frankfurter.dev when the module loads, building a USD-based rate table in memory. Make sure your environment can reach the API the first time you run the tool; afterwards the rates stay cached for the process lifetime. If you need deterministic tests, mock `requests.get` or inject your own rate table before calling `convert_currency`.

## Customizing units & aliases
- Edit `data/units.json` to add new canonical units or tweak factors. Each factor is relative to the unit system's base (meter, liter, gram).
- Edit `data/aliases.json` to accept new spellings or symbols. Keep the canonical keys in sync with `units.json` (for unit modes) and ensure each alias list remains unique.

## Testing
All converters have dedicated pytest suites under `test/`. Run them with:

```bash
pytest
```

This validates numeric conversions, error handling, and temperature guardrails.
