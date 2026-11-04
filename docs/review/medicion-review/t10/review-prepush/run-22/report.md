## Summary and verdict

La rama añade paginación de pedidos y descarga de facturas, pero contiene tres fallos críticos: permite leer archivos fuera del directorio de facturas, omite pedidos al paginar y altera el resultado usado por el dashboard.

**Verdict:** BLOCK

## Critical

#### C1 Lectura de archivos fuera del directorio de facturas
- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** El nombre recibido en la petición se une a la ruta de facturas sin comprobar que el archivo resultante permanezca dentro de ella.
- **Why it fails / scenario:** Una petición a `/invoices?file=../../package.json` puede obtener ese archivo; también expone otros archivos legibles por el proceso.
- **Fix:** Validar los nombres admitidos y rechazar rutas o enlaces simbólicos que salgan del directorio. Añadir pruebas de descarga y de recorrido de directorios.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 La primera página omite los pedidos más recientes
- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** El desplazamiento trata como índice una página numerada desde uno.
- **Why it fails / scenario:** `/orders?page=1&size=10` empieza en el índice 10 y omite los diez pedidos más recientes; la página 3 queda vacía aunque quedan cinco pedidos.
- **Fix:** Calcular `(page - 1) * pageSize` y comprobar los identificadores exactos de la primera página, páginas intermedias y última página.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 El dashboard selecciona el pedido más reciente como el primero
- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** `firstOrder()` depende del antiguo orden ascendente de `listOrders()`, que ahora se ha invertido.
- **Why it fails / scenario:** El pedido usado para «cliente desde» cambia del ID 1 al ID 25.
- **Fix:** Adaptar `firstOrder()` para seleccionar el pedido más antiguo y añadir una prueba de regresión.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Queda una salida de depuración en cada petición de pedidos
- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** La ruta de paginación conserva un `console.log` identificado como `DEBUG`.
- **Why it fails / scenario:** Cada petición de paginación escribe información de diagnóstico en los registros.
- **Fix:** Eliminar la salida de depuración.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 El endpoint de facturas no tiene pruebas
- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** La nueva lectura de archivos y su gestión de errores no tienen cobertura.
- **Why it fails / scenario:** La suite pasa aunque falle la descarga o una ruta controlada por la petición escape del directorio.
- **Fix:** Añadir pruebas del endpoint para una factura válida, un archivo inexistente y los intentos de recorrido de directorios.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 TODO de caché sin referencia de seguimiento
- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** El nuevo TODO no incluye una referencia a una tarea.
- **Why it fails / scenario:** La propuesta de caché queda sin un mecanismo de seguimiento.
- **Fix:** Eliminarlo o vincularlo a una tarea.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) limita el tamaño solicitado de página a 50.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → pasa; un archivo de pruebas, sin fallos.
- Semgrep: no se pudo ejecutar; el entorno no dispone de un directorio temporal utilizable y no hay herramienta MCP de Semgrep disponible.
- Callers: se revisaron tres puntos de llamada fuera del diff de dos símbolos modificados; no se encontraron consumidores externos de la ruta en el repositorio.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.
- El árbol de trabajo estaba limpio; no se modificaron archivos.

REVIEW_RESULT: BLOCK critical=3 required=2 uncertain=0