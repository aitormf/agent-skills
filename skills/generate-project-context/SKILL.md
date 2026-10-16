---
name: generate-project-context
description: Crea o actualiza los ficheros de contexto de un proyecto (AGENTS.md, docs/ARCHITECTURE.md con sus principios innegociables, CONTRIBUTING.md, ADRs, SECURITY.md y plantilla de PR) mediante una entrevista guiada. Úsala al arrancar un proyecto, al adoptar agentes en un proyecto existente, o cuando pidan una "constitución", principios del proyecto, reglas de arquitectura o documentación para agentes.
---

# Contexto del proyecto

Ayuda a la persona a decidir y dejar por escrito las reglas estables del proyecto, cada una en el fichero que le corresponde. **Las decisiones las toma la persona**: tú lees, propones opciones concretas y redactas.

Sustituye a la `constitution.md` de Spec Kit. Todo su contenido tiene un sitio mejor:

| Contenido | Fichero | Lo leen |
|---|---|---|
| Stack, capas, reglas de dependencia, **principios innegociables**, glosario | `docs/ARCHITECTURE.md` | Personas y agentes; `spec-to-plan` y `review-spec` comprueban los principios |
| Calidad, ramas, commits, PRs, revisión, uso de IA | `CONTRIBUTING.md` | Personas (y agentes, por enlace) |
| El porqué de cada decisión estructural y las alternativas descartadas | `docs/adr/NNNN-*.md` | Ambos, bajo demanda |
| Comandos, límites, convenciones no obvias, mapa de la documentación | `AGENTS.md` (+ `CLAUDE.md` con `@AGENTS.md`) | Agentes, en **cada** sesión |
| Cómo informar de vulnerabilidades, política de agentes | `SECURITY.md` | Personas |

Plantillas en `assets/es/` (y `assets/en/` si el proyecto se documenta en inglés). Cada una explica en su comentario inicial cómo rellenarla.

## Reglas

- **No dupliques.** Si algo ya está en `pyproject.toml`, en la CI o en un linter, enlázalo; no lo copies. Si un principio aparece en dos ficheros, acabará contradiciéndose: los principios viven solo en `ARCHITECTURE.md`.
- **`AGENTS.md` corto:** menos de 150 líneas. Es un mapa que enlaza; no contiene. Para cada línea: "¿si la quito, el agente se equivocaría?". Si no, fuera.
- **Lo que se puede comprobar con una herramienta, se comprueba con una herramienta.** Para cada principio, pregunta cómo se verifica (lint, import-linter, test, CI, revisión) y anótalo en su columna.
- **Nada volátil:** ni estado del sprint ni TODOs. Eso va en el tracker o en `docs/plans/`.
- Enseña cada fichero completo (o el diff, si ya existe) y escribe solo después de que la persona lo apruebe.

## Proceso

### 1. Leer el proyecto

Antes de preguntar nada, lee: manifiestos (`pyproject.toml`, `package.json`, `go.mod`…), `README.md`, los ficheros de contexto que ya existan, `.github/workflows/`, la config de linters y la estructura de carpetas. Usa lo que encuentres para **proponer respuestas** en lugar de preguntar en abierto.

Decide el modo y díselo a la persona:

- **Greenfield** (sin código o casi): `ARCHITECTURE.md` es **prescriptivo**, cómo será.
- **Brownfield**: `ARCHITECTURE.md` es **descriptivo**, cómo es hoy. El ideal va en ADRs y en los trinquetes de las herramientas. Si ya existen ficheros de contexto, solo preguntas por los huecos y propones diffs.
- **Migración desde una `constitution.md`**: reparte su contenido según la tabla de arriba y propón borrarla o reducirla a un enlace.

### 2. Entrevista por rondas

Una categoría cada vez. Para cada pregunta, ofrece opciones concretas (A, B, "dejar abierta", "otra"). Si los ficheros ya la responden, pide confirmación en lugar de preguntar. Si una categoría no aplica (p. ej. no hay base de datos), sáltala y dilo. Al final de cada ronda, resume lo decidido.

| Ronda | Qué se decide | Destino |
|---|---|---|
| 1. Propósito | Qué es el proyecto y qué queda fuera; tipo (app, servicio, librería, CLI) | `ARCHITECTURE.md` §1, `README.md` |
| 2. Stack y arquitectura | Lenguaje, framework, persistencia, infraestructura; capas o módulos y qué puede importar qué | `ARCHITECTURE.md` §2–4, un ADR por decisión estructural |
| 3. Principios innegociables | 5–10 reglas estables y verificables: por qué y cómo se comprueba cada una | `ARCHITECTURE.md` §5 |
| 4. Calidad | Test primero o después, cobertura mínima, tipado, qué no se mockea nunca | `CONTRIBUTING.md` §5; si es innegociable, también un principio |
| 5. Seguridad | Autenticación, datos sensibles, validación de entradas, cumplimiento normativo | `ARCHITECTURE.md` §10, `SECURITY.md` |
| 6. Proceso | Ramas, Conventional Commits, merge o squash, aprobaciones, tamaño de PR, herramientas de IA permitidas | `CONTRIBUTING.md` §4, §6–7 |
| 7. Dependencias | Política para añadirlas, librerías prohibidas, construir o comprar | Principio (si es innegociable) o `CONTRIBUTING.md` |
| 8. Para el agente | Comandos (el de verificación es obligatorio), convenciones no obvias, zonas críticas o frágiles (brownfield), límites (siempre / preguntar / nunca) | `AGENTS.md` |

En la ronda 8, el **comando de verificación** es el contrato con el resto de skills (`plan-to-tasks`, `implement`, review). Si no existe, propón `setup-guardrails-python` (u otra equivalente para el lenguaje) o déjalo como pregunta abierta en `AGENTS.md`.

### 3. Redactar y escribir

Orden: `ARCHITECTURE.md` → ADRs → `CONTRIBUTING.md` → `SECURITY.md` → `AGENTS.md`. `AGENTS.md` va al final porque enlaza a todos.

- Parte de la plantilla de `assets/`. Borra las secciones que no apliquen todavía; no las dejes vacías.
- ADRs: copia `ADR.md` como `docs/adr/0000-plantilla.md` y `adr-README.md` como `docs/adr/README.md`. Crea un ADR por cada decisión estructural de las rondas 2–3. Brownfield: solo 3–5 retroactivos, de lo que más se cuestiona, con las alternativas descartadas.
- `AGENTS.md` debe incluir:
  - la línea de "Planificación": revisar el plan contra los principios de `docs/ARCHITECTURE.md` antes de implementar;
  - un enlace a `CONTRIBUTING.md` para el proceso.
- `CLAUDE.md` contiene solo `@AGENTS.md`, salvo que ya tenga contenido. En ese caso, propón moverlo a `AGENTS.md`.
- `pull_request_template.md` va en `.github/`. Ofrécelo, no lo impongas.

### 4. Cierre

Lista los ficheros creados o cambiados y las preguntas que quedaron abiertas. Recuerda a la persona:

- `AGENTS.md` se revisa cada mes y se poda, sobre todo al cambiar de modelo.
- `ARCHITECTURE.md` se contrasta con el código cada trimestre.
- Cada error que el agente repita se convierte en una regla de herramienta o, como último recurso, en una línea de "Trampas conocidas".
