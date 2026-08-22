#!/usr/bin/env python3
"""Check that every manuscript includegraphics file exists on disk."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
MANUSCRIPT_DIR = PROJECT_DIR / "manuscript"
GRAPHIC_ROOTS = [
    MANUSCRIPT_DIR / "figures",
    PROJECT_DIR / "alphafold_figures",
    PROJECT_DIR / "results" / "open_data",
]
INCLUDE_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def resolve_graphic(name: str) -> Path | None:
    path = Path(name)
    candidates = [path] if path.is_absolute() else []
    if not path.suffix:
        for ext in (".pdf", ".png", ".jpg"):
            candidates.extend(root / f"{name}{ext}" for root in GRAPHIC_ROOTS)
    else:
        candidates.extend(root / name for root in GRAPHIC_ROOTS)
        candidates.append(MANUSCRIPT_DIR / name)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    tex_files = [MANUSCRIPT_DIR / "main.tex", *sorted((MANUSCRIPT_DIR / "sections").glob("*.tex"))]
    missing: list[str] = []
    found = 0
    for tex in tex_files:
        text = tex.read_text(encoding="utf-8")
        for match in INCLUDE_RE.finditer(text):
            name = match.group(1).strip()
            if resolve_graphic(name) is None:
                missing.append(f"{tex.relative_to(PROJECT_DIR)}: {name}")
            else:
                found += 1

    print(f"Resolved {found} includegraphics paths.")
    if missing:
        print("Missing graphics:")
        for item in missing:
            print(f"  - {item}")
        return 1
    print("All manuscript graphics are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
