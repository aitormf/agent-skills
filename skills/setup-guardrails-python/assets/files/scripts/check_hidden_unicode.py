#!/usr/bin/env python3
# scripts/check_hidden_unicode.py
"""Falla si los ficheros contienen caracteres Unicode invisibles o de control bidireccional."""

import sys
import unicodedata
from pathlib import Path


def is_suspicious(ch: str) -> bool:
    cp = ord(ch)
    return (
        unicodedata.category(ch) == "Cf"  # zero-width, bidi, etiquetas (U+E00xx), BOM…
        or 0xFE00 <= cp <= 0xFE0F  # selectores de variación
        or 0xE0100 <= cp <= 0xE01EF  # selectores de variación suplementarios
    )


def main(paths: list[str]) -> int:
    failed = False
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for ch in line:
                if is_suspicious(ch):
                    name = unicodedata.name(ch, "desconocido")
                    print(f"{path}:{lineno}: carácter invisible U+{ord(ch):04X} ({name})")
                    failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
