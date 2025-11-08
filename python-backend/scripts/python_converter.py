"""
Wrapper script that exposes the Conversor interactive CLI inside the portfolio
Python runner. It bootstraps the vendored project and delegates to its REPL.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_project() -> Path:
    """Insert the vendored repo into sys.path so we can import its modules."""
    project_dir = Path(__file__).resolve().parent / "python_converter_project"
    if not project_dir.exists():
        raise FileNotFoundError(
            "python_converter_project directory is missing inside scripts/"
        )

    sys.path.insert(0, str(project_dir))
    return project_dir


def main() -> None:
    try:
        _bootstrap_project()
        from interactive import main as interactive_main  # type: ignore
    except ModuleNotFoundError as exc:
        print("Could not import the Conversor interactive module:", exc, flush=True)
        print(
            "Verify that python_converter_project/ is cloned and its dependencies "
            "are installed.",
            flush=True,
        )
        return
    except FileNotFoundError as exc:
        print(str(exc), flush=True)
        return
    except Exception as exc:  # pragma: no cover - defensive logging path
        print("Unexpected initialization error:", exc, flush=True)
        return

    print("Launching Conversor interactive mode...", flush=True)
    interactive_main()


if __name__ == "__main__":
    main()
