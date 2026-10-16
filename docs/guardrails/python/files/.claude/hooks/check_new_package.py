#!/usr/bin/env python3
# .claude/hooks/check_new_package.py
"""PreToolUse: antes de `uv add`, comprueba que cada paquete existe en PyPI y tiene historial."""

import json
import re
import shlex
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime

MIN_AGE_DAYS = 90
FLAGS_WITH_VALUE = {"--group", "--optional", "--extra", "-r", "--requirements", "--index", "--package"}
SEPARATORS = {"&&", "||", ";", "|", "&"}


def requested_packages(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)  # separa ";", "&&", "|"… aunque vayan pegados
    except ValueError:
        return []
    packages = []
    for i in range(len(tokens) - 1):
        if tokens[i] != "uv" or tokens[i + 1] != "add":
            continue
        j = i + 2
        while j < len(tokens) and tokens[j] not in SEPARATORS:
            token = tokens[j]
            if token in FLAGS_WITH_VALUE:
                j += 1
            elif not token.startswith(("-", ".", "/", "git+", "http://", "https://")):
                name = re.split(r"[\[<>=!~;@ ]", token, maxsplit=1)[0]
                if name:
                    packages.append(name)
            j += 1
    return packages


def first_upload(name: str) -> datetime | None:
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=10) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    uploads = [f["upload_time_iso_8601"] for files in data["releases"].values() for f in files]
    if not uploads:
        return None
    return min(datetime.fromisoformat(u.replace("Z", "+00:00")) for u in uploads)


def main() -> int:
    event = json.load(sys.stdin)
    command = event.get("tool_input", {}).get("command", "")
    problems = []
    for name in requested_packages(command):
        try:
            first = first_upload(name)
        except Exception as exc:  # sin red: avisar, no bloquear
            print(f"Aviso: no se pudo comprobar '{name}' en PyPI ({exc}).", file=sys.stderr)
            continue
        if first is None:
            problems.append(f"'{name}' no existe en PyPI o no tiene versiones: posible paquete alucinado.")
        elif (datetime.now(UTC) - first).days < MIN_AGE_DAYS:
            problems.append(f"'{name}' se publicó por primera vez el {first:%Y-%m-%d} (hace menos de {MIN_AGE_DAYS} días).")
    if problems:
        print(
            "Dependencia bloqueada:\n- " + "\n- ".join(problems)
            + "\nComprueba el nombre exacto y confírmalo con una persona antes de añadirlo.",
            file=sys.stderr,
        )
        return 2  # exit 2 = bloquear la herramienta y devolver el motivo al agente
    return 0


if __name__ == "__main__":
    sys.exit(main())
