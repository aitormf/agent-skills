# Guía de desarrollo con IA — Personal

Oct 23, 2026 · @Aitor

## Propósito

Trabajando solos aplicamos la misma regla que en equipo: el proceso se ajusta al tamaño y al riesgo de la tarea. Cambian dos cosas: nadie más revisa nuestro trabajo, y podemos permitirnos tirar código.

| Aspecto | En equipo | En personal | Por qué |
| --- | --- | --- | --- |
| Revisión | Revisión por pares del plan y del diff | Autorrevisión: tests y un agente revisor con contexto limpio | Sin un segundo par de ojos, los tests y la revisión con contexto nuevo son la única red ([Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/)). |
| Código desechable | Casi nunca | Prototipos y experimentos frecuentes | El vibe coding vale para lo que se va a tirar ([Karpathy](https://karpathy.bearblog.dev/sequoia-ascent-2026/)). |
| Spec | Spec corta compartida o `.feature` revisado por negocio | Notas en un issue o en el propio repo | Nadie más la tiene que leer; basta con que nos sirva a nosotros y al agente ([Willison, issue-driven](https://larryhudson.io/issue-driven-development/)). |
| BDD y DDD | Three Amigos, context mapping entre equipos | Versión ligera: ejemplos propios y glosario | Somos a la vez negocio y desarrollo; la ceremonia sobra, el pensamiento no. |

La guía de equipos sigue siendo la referencia para el porqué general; aquí solo cambia lo que depende de trabajar solos.

## Por qué tampoco usamos SDD completo

Trabajando solos, el SDD completo cuesta aún más, porque todo el markdown que genera lo tenemos que revisar nosotros. Las limitaciones son las mismas que en equipo:

- **Más lento sin ganar calidad:** 33 min y 2.577 líneas de markdown para 689 líneas de código, frente a 8 min con prompting iterativo ([Hidde de Smet](https://hiddedesmet.com/the-hidden-costs-of-spec-driven-development)). En otra prueba, el autor no llegó a terminar una feature mediana con Spec Kit ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)).
- **Revisión que se cambia de sitio:** «I'd rather review code than all these markdown files» ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)). Solos, acabamos aprobando sin leer.
- **Supone que no se aprende al implementar:** en proyectos personales, que suelen ser exploratorios, es justo lo contrario ([Kent Beck y Fowler](https://martinfowler.com/fragments/2026-01-08.html), [Isoform](https://isoform.ai/blog/the-limits-of-spec-driven-development)).
- **Satura el contexto del agente:** specs largas degradan el modelo ([Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg), [Osmani](https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents)).

**Por qué lo tenemos en cuenta:** varios practicantes que probaron Spec Kit en herramientas pequeñas lo encontraron «demasiado lento, demasiados retoques antes de ver código» ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html), [Hacker News](https://news.ycombinator.com/item?id=45935763)).

## Principios base

Aplicamos las prácticas técnicas de XP (Extreme Programming) con el agente como pareja de programación. Son las mismas que en la guía de equipos; lo que no aplicamos trabajando solos son las prácticas sociales (revisión por pares, propiedad colectiva), que sustituimos por autorrevisión. Añadimos un principio propio: decidir de antemano si el código es desechable.

1. **Decide antes de empezar si es desechable o si va a durar.**
   - Por qué: el vibe coding es aceptable para prototipos que se tiran (un spike de XP), no para lo que vas a mantener. Lo profesional es código revisado, probado y entendido ([Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/), [Karpathy](https://karpathy.bearblog.dev/sequoia-ascent-2026/)).
2. **Si va a durar, el código manda.** El comportamiento vive en tests, la estructura en tests de arquitectura y la calidad del LLM en evaluaciones. Las notas y las issues explican el porqué.
   - Por qué: un test avisa cuando el código se desfasa; unas notas no ([Fowler](https://martinfowler.com/fragments/2026-01-08.html), [Hidde de Smet](https://hiddedesmet.com/the-hidden-costs-of-spec-driven-development)).
3. **Feedback rápido: ver código funcionando cuanto antes.**
   - Por qué: en lo exploratorio, lo que aprendes al implementar cambia el plan ([Kent Beck y Fowler](https://martinfowler.com/fragments/2026-01-08.html)).
4. **Pasos pequeños y commit tras cada uno.**
   - Por qué: sin otra persona que revise, un diff pequeño es lo único que podemos revisar de verdad, y un commit nos permite volver atrás si el agente se desvía ([Osmani](https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents)).
5. **El agente es la pareja; tú piensas y respondes del resultado.** En TDD, tú defines o revisas los tests y el agente los hace pasar sin tocarlos.
   - Por qué: «Do not outsource the thinking» ([Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg)); si el agente escribe tests y código, el código se valida a sí mismo ([Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/)).
6. **Lo no determinista se valida con evaluaciones.** Lo que decide un LLM se mide con casos reales y un umbral mínimo de acierto.
   - Por qué: la misma entrada puede dar salidas distintas, y un test exacto fallaría al azar.

## Cómo combinamos las metodologías

No adoptamos ninguna metodología entera: de cada una tomamos la pieza que resuelve un problema concreto, en su versión para una persona. El [ejemplo práctico del agente de dictado](https://claude.ai/artifact/9xYMDfS1ezcoZmcf3QFtpK) las aplica de principio a fin.

| Problema | Pieza que usamos | De dónde viene | Por qué |
| --- | --- | --- | --- |
| No sabemos bien qué construir | Spike desechable de una tarde | XP | Lo que se aprende implementando cambia el plan ([Fowler](https://martinfowler.com/fragments/2026-01-08.html)) |
| Encontrar reglas y casos límite | Example Mapping propio y escenarios Dado/Cuando/Entonces | BDD | Los ejemplos se convierten en tests; sin reuniones porque somos negocio y desarrollo |
| Dividir y nombrar | Módulos por contexto y glosario en `AGENTS.md` | DDD | El agente razona con nuestro vocabulario y lee menos código |
| Organizar el trabajo | Kanban con una tarea en curso y un plazo máximo (appetite) | Kanban y Shape Up | Sin ceremonias; el plazo evita que el proyecto personal no acabe nunca |
| Trabajar con el agente | Plan mode o Research → Plan → Implement según el riesgo | [Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg), [Instil](https://instil.co/blog/spec-driven-development-is-dead-long-live-plan-mode) | El plan es nuestro único punto de control |
| Escribir código que se pueda mantener | TDD ping-pong y commits pequeños | XP | El agente no puede ajustar los tests a su código |
| Validar lo que decide el LLM | Evaluaciones con umbrales y casos reales | — | Un test exacto falla al azar con salidas no deterministas |

**Criterio para decidir: el código manda.** Entre dos opciones, gana la que deja la verdad en algo ejecutable (tests, tests de arquitectura, evaluaciones); las notas explican el porqué.

**Si piensas abrirlo a un equipo:** las técnicas no cambian. Usa desde el principio ramas cortas con PR y la estructura `AGENTS.md` + `CONTRIBUTING.md` + `docs/architecture.md` de la guía de equipos, para no cambiar de flujo al migrar.

## Elegir el proceso según la tarea

En personal añadimos un nivel por debajo de todo, el código desechable, donde el vibe coding es válido. El resto de niveles son los de la guía de equipos, con la revisión hecha por nosotros mismos.

| Tipo de tarea | Proceso | Por qué |
| --- | --- | --- |
| Prototipo, experimento o script de un solo uso | Vibe coding: pedir, probar, tirar | Si se va a tirar, revisar el código no compensa; vibe coding «sube el suelo» para lo rápido ([Karpathy](https://karpathy.bearblog.dev/sequoia-ascent-2026/)). |
| Trivial en un proyecto que vas a mantener | Prompt directo y leer el diff | Un plan sería más largo que el diff ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)). |
| Bug con causa clara | Test que reproduce el bug, luego el arreglo | El test demuestra el arreglo y evita que el bug vuelva ([Fowler](https://martinfowler.com/fragments/2026-01-08.html)). |
| Bug de causa desconocida o issue en código que no recuerdas | RPI ligero con autorrevisión (siguiente sección) | Sin investigar, el agente arregla el síntoma ([Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg)). |
| Feature mediana | Plan mode con el plan guardado en el issue o en un fichero | El plan es nuestro único punto de control; guardarlo permite retomarlo otro día y en contexto limpio ([Instil](https://instil.co/blog/spec-driven-development-is-dead-long-live-plan-mode), [Willison](https://larryhudson.io/issue-driven-development/)). |
| Feature grande o con reglas delicadas (dinero, datos personales) | Escenarios Dado/Cuando/Entonces convertidos en tests + plan, por fases | Aquí sí compensa fijar intención y casos límite antes de generar código ([Osmani](https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents), [Glukhov](https://www.glukhov.org/ai-devtools/vibe-coding/spec-driven-development-vs-vibe-coding/)). |

**Regla de oro:** si un prototipo empieza a usarse de verdad, deja de ser desechable. Antes de seguir, añade tests a lo que importa y sube de nivel.

## RPI ligero con autorrevisión

Es el mismo RPI ligero de la guía de equipos, con un cuarto paso que sustituye la revisión por pares. Sigue el flujo Research → Plan → Implement de [Dex Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg).

1. **Research.** Prompt: «Investiga por qué pasa X. No toques código; explícame la causa y qué ficheros intervienen».
   - Por qué: obliga al agente a leer el código real y evita arreglar el síntoma.
2. **Plan.** Activa plan mode (en Claude Code, Shift+Tab) o pide un plan de 3–5 pasos. Léelo.
   - Por qué: solos, el plan es el único punto donde paramos a pensar antes de que haya código ([Instil](https://instil.co/blog/spec-driven-development-is-dead-long-live-plan-mode)).
3. **Implement.** Prompt: «Primero un test que reproduzca el problema y falle; luego el arreglo; luego pasa los tests». Commit al terminar.
   - Por qué: el test es la spec ejecutable ([Fowler](https://martinfowler.com/fragments/2026-01-08.html)), y el commit es nuestro punto de vuelta atrás ([Osmani](https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents)).
4. **Autorrevisión.** Antes del merge, pide una revisión del diff en un contexto limpio (`/clear`, un subagente o `/code-review`) y lee el diff tú.
   - Por qué: el agente que escribió el código arrastra sus propias suposiciones; un contexto nuevo es lo más parecido a otro revisor. La responsabilidad sigue siendo nuestra ([Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/)).

**Si se tuerce:** para, haz `/clear` y vuelve a Research con lo que ya sabes. Por qué: un contexto lleno de intentos fallidos degrada el modelo ([Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg)).

## BDD y DDD en versión ligera

De BDD y DDD nos quedamos con el pensamiento y dejamos la ceremonia: ejemplos concretos antes de programar reglas delicadas, y un vocabulario del dominio que el agente conozca. Las explicaciones completas están en las notas `metodologias/BDD.md` y `metodologias/DDD.md`.

| Práctica | Qué hacemos | Qué dejamos | Por qué |
| --- | --- | --- | --- |
| Example Mapping (BDD) | Antes de una regla delicada, escribimos reglas, ejemplos concretos y preguntas abiertas; podemos pedir al agente que proponga casos límite | Las reuniones Three Amigos | Somos negocio y desarrollo a la vez; lo valioso son los ejemplos, no la reunión. |
| Escenarios ejecutables (BDD) | Tests con nombres de negocio (`reembolsa todo si se cancela con más de 1h`) o un `.feature` si la regla es compleja | Gherkin obligatorio y automatización por UI | Sin negocio que lea el Gherkin, la capa de lenguaje natural es coste extra. |
| Lenguaje ubicuo (DDD) | Un glosario corto del dominio en `CLAUDE.md` o `AGENTS.md` | Talleres de Event Storming | El agente nombra y razona como el dominio, y gasta menos contexto adivinando. |
| Value objects y agregados (DDD) | Para dinero, fechas y reglas que no se pueden saltar | Repositorios, factories y CQRS en proyectos pequeños | Protegen las reglas frente a código generado sin añadir capas que no necesitamos. |
| Bounded contexts (DDD) | Separar en módulos las partes con significado propio | Context mapping entre equipos | Un módulo pequeño acota el contexto que el agente tiene que leer ([Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg)). |

**Regla de seguridad:** si el agente escribe los ejemplos, los revisamos nosotros antes de que implemente. Por qué: si el agente genera los tests y el código, el código se valida a sí mismo.

## Señales para subir o bajar de nivel

Si aparece alguna de estas señales a mitad de tarea, cambiamos de nivel en la tabla de «Elegir el proceso».

| Señal | Diagnóstico | Qué hacer | Por qué |
| --- | --- | --- | --- |
| El plan es más largo que el diff | Demasiado proceso | Bajar de nivel | Revisar documentos cuesta más que revisar el código ([Böckeler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)). |
| Ya sabías la solución antes de empezar | Demasiado proceso | Prompt directo | El pensamiento ya está hecho ([Glukhov](https://www.glukhov.org/ai-devtools/vibe-coding/spec-driven-development-vs-vibe-coding/)). |
| Un prototipo empieza a usarse de verdad | Ya no es desechable | Añadir tests y subir de nivel | El vibe coding no vale para lo que hay que mantener ([Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/)). |
| No entiendes el código que ha escrito el agente | Falta proceso | Parar, pedir que lo explique y volver a plan mode | Si no lo entiendes, no puedes responder de él ([Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/)). |
| El agente toca ficheros que no esperabas | Falta proceso | Subir a RPI o plan mode | Sin plan revisado no hay punto de control ([Instil](https://instil.co/blog/spec-driven-development-is-dead-long-live-plan-mode)). |
| Llevas tres intentos corrigiendo con prompts | Contexto degradado | `/clear` y volver a Research | El rendimiento cae con el contexto lleno de ruido ([Horthy](https://www.youtube.com/watch?v=rmvDxxNubIg)). |

## Fuentes

Todas se consultaron en octubre de 2026. Las opiniones de Karpathy y Willison proceden en parte de crónicas de terceros. Las prácticas de BDD y DDD se basan en las notas locales `metodologias/`.

| Autor | Fuente | Para qué la usamos aquí |
| --- | --- | --- |
| Birgitta Böckeler (Thoughtworks) | [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) | Coste de revisar specs frente a código |
| Kent Beck y Martin Fowler | [Fragments: January 8 (2026)](https://martinfowler.com/fragments/2026-01-08.html) | Feedback rápido y tests como spec |
| Dex Horthy (HumanLayer) | [No Vibes Allowed (vídeo)](https://www.youtube.com/watch?v=rmvDxxNubIg) | Research → Plan → Implement y gestión del contexto |
| Addy Osmani | [How to write a good spec for AI agents](https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents) | Specs mínimas, pasos pequeños y commits |
| Simon Willison | [Vibe engineering](https://simonwillison.net/2025/Oct/7/vibe-engineering/) · [Issue-driven development (Larry Hudson)](https://larryhudson.io/issue-driven-development/) | Responsabilidad sobre el código; issues como spec |
| Andrej Karpathy | [Sequoia Ascent 2026](https://karpathy.bearblog.dev/sequoia-ascent-2026/) | Cuándo vale el vibe coding |
| Instil | [Spec-Driven Development is dead, long live plan mode](https://instil.co/blog/spec-driven-development-is-dead-long-live-plan-mode) | Plan mode como spec ligera |
| Hidde de Smet | [The hidden costs of spec-driven development](https://hiddedesmet.com/the-hidden-costs-of-spec-driven-development) | Medidas de coste del SDD |
| Scott Logic | [Putting Spec Kit Through Its Paces](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html) | SDD en proyectos pequeños |
| Hacker News | [Spec-Driven Development: The Waterfall Strikes Back](https://news.ycombinator.com/item?id=45935763) | Experiencias con herramientas pequeñas |
| Isoform | [The Limits of Spec-Driven Development](https://isoform.ai/blog/the-limits-of-spec-driven-development) | SDD en trabajo exploratorio |
| Rost Glukhov | [SDD vs Vibe Coding](https://www.glukhov.org/ai-devtools/vibe-coding/spec-driven-development-vs-vibe-coding/) | Specs de una pantalla |

Aplicación de esta guía de principio a fin: [Ejemplo práctico: agente de dictado y notas](https://claude.ai/artifact/9xYMDfS1ezcoZmcf3QFtpK).
