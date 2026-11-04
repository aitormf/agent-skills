## Summary and verdict

La rama añade paginación a `/orders` y descarga de facturas, pero la primera página omite pedidos y el endpoint de facturas permite leer archivos fuera del directorio previsto. El nuevo orden de `listOrders()` también rompe un consumidor existente.

**Verdict:** BLOCK

## Critical

#### C1 Lectura de archivos fuera del directorio de facturas
- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** El nombre recibido en la petición se usa para construir una ruta de lectura sin comprobar que permanezca en el directorio de facturas.
- **Why it fails / scenario:** Un cliente puede pedir `/invoices?file=../../package.json` y recibir ese archivo. Otros recorridos permiten acceder a archivos legibles por el proceso.
- **Fix:** Restringir los nombres admitidos y comprobar que la ruta real permanezca dentro del directorio de facturas; añadir pruebas de recorrido de directorios y enlaces simbólicos.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 La primera página omite los pedidos más recientes
- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** El desplazamiento usa `page * pageSize`, aunque las páginas empiezan en 1.
- **Why it fails / scenario:** La página 1 de tamaño 10 devuelve los pedidos 15–6 en vez de 25–16; con tamaño 50 devuelve una página vacía.
- **Fix:** Calcular el desplazamiento como `(page - 1) * pageSize` y comprobar el contenido exacto de las páginas.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 El cambio de orden rompe `firstOrder`
- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** Este consumidor espera que `listOrders()` empiece por el pedido más antiguo, pero ahora empieza por el más reciente.
- **Why it fails / scenario:** `firstOrder()` devuelve el pedido 25 en lugar del 1, incumpliendo su contrato de devolver el más antiguo.
- **Fix:** Adaptar `firstOrder()` al nuevo orden y añadir una prueba de regresión.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 La prueba de paginación acepta resultados incorrectos
- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** La prueba comprueba el tipo, el tamaño máximo y el total, pero no los pedidos devueltos ni el total de la página.
- **Why it fails / scenario:** Tanto el error de C2 como una implementación que devuelva siempre una página vacía pasan la prueba.
- **Fix:** Verificar IDs y totales exactos en la primera página, páginas posteriores y límites, incluido el tamaño máximo.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Faltan pruebas del endpoint de facturas
- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** La nueva ruta de lectura de disco no tiene pruebas de comportamiento ni de entradas maliciosas.
- **Why it fails / scenario:** La suite pasa tanto con el recorrido de directorios de C1 como si fallase la descarga válida.
- **Fix:** Probar una factura válida, un archivo ausente y los intentos de salir del directorio.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Salida de depuración en cada petición
- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Un `console.log` de depuración se ejecuta en cada paginación.
- **Why it fails / scenario:** Las peticiones generan salida de depuración y volumen innecesario en los logs.
- **Fix:** Eliminar la instrucción.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 TODO sin referencia de seguimiento
- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** El nuevo TODO para almacenar facturas en caché no referencia una tarea.
- **Why it fails / scenario:** La mejora queda sin seguimiento.
- **Fix:** Eliminarlo o asociarlo a una tarea.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) limita el tamaño solicitado de página a 50.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → pasó; Node informó de 1 archivo de pruebas, sin fallos.
- Semgrep: el análisis falló porque no había un directorio temporal escribible; no había herramientas Semgrep MCP disponibles.
- Callers: se revisaron los consumidores externos al diff de los contratos modificados; `firstOrder()` resulta afectado.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- El árbol de trabajo estaba limpio.

REVIEW_RESULT: BLOCK critical=3 required=3 uncertain=0