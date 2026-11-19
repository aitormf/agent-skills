#!/usr/bin/env python3
"""The verification of the push, run by the hook and not by the reviewer (D-0061, D-0062).

Usage: verify.py <base> <results file>. Reads `[review] verify` (a list of commands) and `[review] semgrep`
(default true) of the BASE branch's .harness-config.toml, never of the branch under review. Without `verify`
it does nothing. Otherwise it runs each command with `bash -c` from the current directory (the repo root),
in order and without GitHub credentials, then semgrep_added.py, and writes the results file: each command
with its exit code and the last 40 lines of its output, and the Semgrep findings.
Exit 0: green (Semgrep never decides); exit 1: a command failed or went over TIMEOUT seconds (message and
last lines on stderr; the file is not written); exit 2: the config cannot be read."""
import os
import signal
import subprocess
import sys
import tomllib
from pathlib import Path

TIMEOUT = 600
TAIL = 40
SEMGREP = Path(__file__).resolve().parents[2] / "review-context" / "scripts" / "semgrep_added.py"
CREDENTIALS = ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN")


def tail(text):
    return "\n".join(text.splitlines()[-TAIL:])


def run(args, **kwargs):
    """(exit code or None on timeout, output) of args, with its whole process group killed on timeout."""
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               stdin=subprocess.DEVNULL, start_new_session=True, **kwargs)
    try:
        output, _ = process.communicate(timeout=TIMEOUT)
        return process.returncode, output
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        output, _ = process.communicate()
        return None, output


def main(base, out_file):
    shown = subprocess.run(["git", "show", f"{base}:.harness-config.toml"], capture_output=True, text=True) if base else None
    try:
        review = tomllib.loads(shown.stdout if shown and shown.returncode == 0 else "").get("review", {})
        commands, semgrep = review.get("verify", []), review.get("semgrep", True)
        if not isinstance(commands, list) or not all(isinstance(c, str) for c in commands):
            raise ValueError("[review] verify es una lista de comandos")
        if not isinstance(semgrep, bool):
            raise ValueError("[review] semgrep es true o false")
    except (tomllib.TOMLDecodeError, AttributeError, ValueError) as error:
        print(f"review-kit: .harness-config.toml de la rama base no es válido: {error}", file=sys.stderr)
        return 2
    if not commands:
        return 0
    env = {k: v for k, v in os.environ.items() if k not in CREDENTIALS}
    sections = ["# Verificación del hook (la ha ejecutado el hook, no el revisor)"]
    for command in commands:
        code, output = run(["bash", "-c", command], env=env)
        result = f"exit {code}" if code is not None else f"timeout {TIMEOUT} s"
        if code != 0:
            print(f"review-kit: verificación en rojo: {command} ({result})", file=sys.stderr)
            print(tail(output), file=sys.stderr)
            return 1
        sections.append(f"## `{command}` — {result}\n\n```\n{tail(output)}\n```")
    if not semgrep:
        sections.append("## Semgrep\n\nSemgrep: desactivado ([review] semgrep = false en la rama base)")
    else:
        code, output = run([sys.executable, str(SEMGREP), base], env=env)
        text = output.strip() if code == 0 else f"Semgrep: no disponible ({output.strip() or 'sin salida'})"
        sections.append(f"## Semgrep (líneas añadidas)\n\n```\n{text}\n```")
    Path(out_file).write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
