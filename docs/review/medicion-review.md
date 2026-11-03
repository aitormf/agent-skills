# Medición base de la review (T1)

Cuántos tokens gastan y qué encuentran `review-pr` y `review-prepush` **tal como están hoy**, ejecutadas con Codex sobre el sandbox de `tests/review-sandbox/`. Es la referencia con la que comparar el reviewer unificado (cambio `review-unificada`, paso S1). Este documento no saca conclusiones sobre el reviewer unificado: aún no existe.

## Cómo se midió

| | |
|---|---|
| Fecha | 2026-11-03 |
| Codex | `codex-cli 0.165.0` |
| Modelo | `gpt-6.1-terra`, explícito con `-m` (por defecto de `measure.sh`, variable `MODEL`) y registrado en cada `meta.json` |
| Commit del repo | `ebaeec1` (`main` con T14 mergeada). `skills/`, `agents/` y `adapters/` no cambian: la review medida es la de ese commit. La PR añade `build.sh --codex`, `measure.sh` y `summarize.py` |
| Sandbox | `tests/review-sandbox/build.sh --codex`, rama `feature/orders-pagination-invoices` (sin red, sin remoto; el hook `pre-push` no se dispara porque no se hace push) |
| Disposición de Codex | skills en `.agents/skills/` y personas en `.codex/agents/*.toml` del sandbox (comprobado: Codex las lista y lee desde ahí) |
| Ejecución | solo lectura (`-s read-only`), sin `--dangerously-bypass-*` |

Comandos exactos (desde la raíz del repo):

```bash
tests/review-sandbox/build.sh --codex
tests/review-sandbox/measure.sh review-prepush 3
tests/review-sandbox/measure.sh review-pr 3
```

Cada ejecución lanza, dentro de `tests/review-sandbox/repo`:

```bash
codex exec -m gpt-6.1-terra -s read-only --json -o report.md "<prompt>"
```

con estos prompts (`$BRANCH` = `feature/orders-pagination-invoices`):

- `review-pr`: «Ejecuta la skill review-pr (.agents/skills/review-pr/SKILL.md) con los argumentos: $BRANCH main. Usa solo las skills de este proyecto, en .agents/skills/ (también las que ella cite: review-context, review-report, task-done); no leas ~/.agents ni ~/.codex. Los subagentes son los de .codex/agents/. No cambies ningún fichero.»
- `review-prepush`: «Ejecuta la skill review-prepush (.agents/skills/review-prepush/SKILL.md) con los argumentos: main, estando en la rama $BRANCH.» y la misma coletilla.

`codex exec` no tiene comandos de barra: la skill se invoca nombrándola en el prompt.

### De dónde salen las cifras

- `turn.completed` de `--json` da solo el uso de la **sesión principal**. No incluye a los subagentes, y la salida `--json` no muestra su arranque (solo eventos `wait` sin ids).
- Los subagentes sí dejan su propio fichero de sesión en `~/.codex/sessions/`, con su rol, su modelo (`turn_context`) y un `token_usage_record` por llamada a la API. `summarize.py` suma esos registros por agente. Para la sesión principal coinciden exactamente con `turn.completed` (comprobado en las seis ejecuciones: campo `problems` vacío en cada `summary.json`).
- Cada cifra sale de esos registros; no hay estimaciones. «Entrada» incluye la «entrada en caché», como la entrega Codex; «razonamiento» se da tal cual, sin sumarlo a la salida.
- **Modelo de los subagentes:** los 24 hilos de las seis ejecuciones (3 por ejecución de `review-prepush` y 5 por la de `review-pr`, la sesión principal incluida) tienen `gpt-6.1-terra` en su `turn_context`. Los subagentes aparecen además con `effort low` en su `turn_context`; los `.toml` de las personas no declaran modelo ni esfuerzo, así que ese valor no sale del kit (no se ha investigado quién lo fija).

### Límites y cosas a tener en cuenta

- **Semgrep falló en las seis ejecuciones** («no hay directorio temporal escribible» en el sandbox de solo lectura), así que cada informe dice «Semgrep: skipped». Una review real lo ejecutaría si está instalado; aquí no cuenta ni en tokens ni en hallazgos.
- **Skills globales:** la máquina tiene copias antiguas en `~/.agents/skills/` y el plugin `harness` activado en `~/.codex/config.toml`. Para que no se cuelen, el prompt manda usar solo `.agents/skills/` del sandbox y ninguna ejecución ha leído `~/.agents` (comprobado en `events.jsonl`). No se aisló `CODEX_HOME` ni `HOME`.
- Cada comando se ejecutó una sola vez por número: **sin repeticiones ni fallos**. La primera ejecución de cada comando hizo de prueba (arranque de subagentes, modelo, tokens) y cuenta como `run-1`. Antes hubo dos llamadas diminutas a `codex exec` (listar skills y agentes, unos 50.000 tokens de entrada) para comprobar qué ve Codex; no están en las tablas.
- `summarize.py` se escribió después del `run-1` de `review-prepush` (hubo que ver el formato de los registros antes); su `summary.json` se generó a mano con el mismo script sobre los mismos datos.
- Los resultados crudos (`events.jsonl`, `stderr.txt`, informes) quedan en `tests/review-sandbox/results/` (en `.gitignore`) y, en esta máquina, copiados a `/tmp/t1-medicion-raw/`. En el repo van los informes, `summary.json` y `meta.json` de cada ejecución en `docs/review/medicion-review/<comando>/run-<n>/`; en los informes se sustituyó la ruta absoluta del sandbox por `repo/`. No hay secretos en ninguno.
- La duración es de reloj, de principio a fin de `codex exec`.

## Tokens

### `review-prepush`

**run-1** (exit 0, 119 s, 2 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 10 | 348.248 | 313.344 | 3.104 | 59 |
| code-reviewer | 2 | 96.778 | 82.688 | 1.095 | 34 |
| finding-verifier | 3 | 155.051 | 142.208 | 1.425 | 21 |
| **Total** | 15 | **600.077** | **538.240** | **5.624** | **114** |

**run-2** (exit 0, 112 s, 2 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 9 | 299.529 | 260.864 | 3.078 | 27 |
| code-reviewer | 2 | 92.355 | 79.360 | 882 | 30 |
| finding-verifier | 3 | 151.423 | 136.192 | 1.286 | 38 |
| **Total** | 14 | **543.307** | **476.416** | **5.246** | **95** |

**run-3** (exit 0, 107 s, 2 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 9 | 283.694 | 253.952 | 3.294 | 9 |
| code-reviewer | 4 | 104.046 | 74.368 | 1.382 | 0 |
| finding-verifier | 3 | 81.056 | 63.744 | 1.544 | 44 |
| **Total** | 16 | **468.796** | **392.064** | **6.220** | **53** |


### `review-pr`

**run-1** (exit 0, 91 s, 4 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 14 | 474.461 | 447.616 | 3.419 | 108 |
| code-reviewer | 3 | 133.142 | 120.832 | 657 | 86 |
| security-auditor | 2 | 90.603 | 76.288 | 276 | 14 |
| test-engineer | 2 | 85.886 | 76.544 | 408 | 31 |
| finding-verifier | 3 | 146.803 | 134.784 | 715 | 47 |
| **Total** | 24 | **930.895** | **856.064** | **5.475** | **286** |

**run-2** (exit 0, 97 s, 4 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 14 | 569.239 | 528.512 | 3.480 | 106 |
| code-reviewer | 3 | 152.600 | 140.160 | 833 | 8 |
| security-auditor | 3 | 154.328 | 142.080 | 630 | 86 |
| test-engineer | 2 | 95.219 | 87.552 | 488 | 35 |
| finding-verifier | 3 | 167.799 | 155.904 | 797 | 48 |
| **Total** | 25 | **1.139.185** | **1.054.208** | **6.228** | **283** |

**run-3** (exit 0, 86 s, 4 subagentes, modelos vistos: gpt-6.1-terra)

| Agente | Llamadas a la API | Entrada | Entrada en caché | Salida | Razonamiento |
|---|---:|---:|---:|---:|---:|
| sesión principal | 15 | 570.105 | 525.952 | 3.093 | 134 |
| code-reviewer | 3 | 127.130 | 122.112 | 737 | 7 |
| security-auditor | 2 | 86.636 | 80.000 | 286 | 23 |
| test-engineer | 3 | 135.469 | 127.360 | 593 | 44 |
| finding-verifier | 3 | 141.014 | 136.064 | 428 | 43 |
| **Total** | 26 | **1.060.354** | **991.488** | **5.137** | **251** |


### Medias

| Comando | Ejecuciones | Subagentes | Duración (s) | Entrada | Entrada en caché | Salida | Razonamiento | Entrada sin caché |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `review-prepush` | 3 | 2 | 113 | 537.393 | 468.907 | 5.697 | 87 | 68.487 |
| `review-pr` | 3 | 4 | 91 | 1.043.478 | 967.253 | 5.613 | 273 | 76.225 |

Las medias son aritméticas sobre 3 ejecuciones; la variación entre ellas es grande (p. ej. entrada de `review-prepush` entre 468.796 y 600.077), así que sirven de orden de magnitud, no de cifra exacta.

## Qué encuentran

Puntuado **a mano**, leyendo cada `report.md` contra `tests/review-sandbox/EXPECTED.md`. Criterio: un bug cuenta si un hallazgo (o el arreglo de otro) lo señala con su causa. B2 exige señalar que el test no comprueba el contenido de la página; si solo lo menciona de pasada en el arreglo de B1 se anota «parcial» y no cuenta. B8 cuenta solo si propone un remedio con nombre (*collapse duplicate branches*, *explicit dispatcher*…), como pide su fila. Un señuelo aparece si sobrevive como hallazgo.

| | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | D1 | D2 | D3 | Bugs detectados |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `review-prepush` run-1 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-prepush` run-2 | sí | no | sí | sí | sí | sí | no | no | no | no | no | no | 5/9 |
| `review-prepush` run-3 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| **`review-prepush`, de 3** | 3 | 2 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 5,7 de media |
| `review-pr` run-1 | sí | parcial | sí | no | no | sí | sí | no | no | no | no | no | 4/9 |
| `review-pr` run-2 | sí | sí | sí | sí | sí | sí | no | no | no | no | no | no | 6/9 |
| `review-pr` run-3 | sí | parcial | sí | sí | no | sí | no | no | no | no | no | no | 4/9 |
| **`review-pr`, de 3** | 3 | 1 (+2 parcial) | 3 | 2 | 1 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 4,7 de media |

Notas por ejecución:

- **`review-prepush` run-1:** además un hallazgo no previsto en `EXPECTED.md`, C4 «el PDF de ejemplo no es un PDF válido» (Critical), sobre `data/invoices/2026-001.pdf`, que es un fichero de prueba mínimo. Veredicto BLOCK.
- **`review-prepush` run-2 y run-3:** veredicto BLOCK; el B2 de run-2 no aparece (solo pide tests del endpoint `/invoices`).
- **`review-pr` run-1:** B2 parcial (R3 critica que el test no comprueba `pageTotal`; el arreglo de C2 pide ids exactos, pero no dice que el test actual pase con el bug). B7 sí: R1 nombra `sumTotals` y propone un módulo común sin ciclo. Tier 2, `CHANGES`.
- **`review-pr` run-2:** B4 y B5 sí; sin B7. Tier 2.
- **`review-pr` run-3:** B2 parcial (la verificación dice «the pagination test gap was folded into C2» y el arreglo de C2 pide ids exactos, sin hallazgo propio). Tier 2.
- **B8 y B9 no aparecen en ninguna de las seis ejecuciones; B7 solo en una.** Ningún señuelo (D1–D3) sobrevive en ninguna.
- Fuera de `EXPECTED.md`, en todas las ejecuciones aparece «falta de test del endpoint `/invoices`» (lo que `EXPECTED.md` da por discutible/aceptable) y, en ninguna, «distinguir ENOENT» como Optional.
- Los `.toml` de las personas y las skills se leyeron de `.codex/agents/` y `.agents/skills/` del sandbox.
