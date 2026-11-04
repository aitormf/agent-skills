## Summary and verdict

La rama añade paginación a `/orders` y descarga de facturas, pero la paginación omite la primera página y la descarga permite leer archivos fuera del directorio de facturas. El cambio de orden también altera el resultado de `firstOrder()`.

**Verdict:** BLOCK

## Critical

#### C1 La descarga de facturas permite leer otros archivos

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** La ruta de lectura incorpora el parámetro de la petición sin limitarlo al directorio de facturas.
- **Why it fails / scenario:** Un cliente puede pedir `/invoices?file=../../src/orders.js` y recibir un archivo legible fuera de ese directorio.
- **Fix:** Restringir los nombres a archivos PDF permitidos y comprobar que la ruta resuelta permanece dentro del directorio de facturas.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 La paginación omite la primera página

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** El desplazamiento trata el número de página como si empezara en cero.
- **Why it fails / scenario:** `page=1&size=10` empieza en el índice 10; con `page=1&size=50` devuelve una página vacía.
- **Fix:** Calcular el desplazamiento como `(page - 1) * pageSize`.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 La función que busca el primer pedido devuelve el más reciente

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** Esta función existente depende del orden ascendente que antes devolvía `listOrders()`.
- **Why it fails / scenario:** `firstOrder()` devuelve ahora el pedido 25 en lugar del más antiguo, el 1.
- **Fix:** Seleccionar el pedido más antiguo teniendo en cuenta el nuevo contrato de `listOrders()`.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 La prueba de paginación acepta páginas incorrectas

- **Location:** [test/orders.test.js:13](repo/test/orders.test.js:13)
- **Problem:** La prueba solo comprueba el tipo del array, su longitud máxima y el total.
- **Why it fails / scenario:** La implementación actual devuelve una página desplazada y aun así supera la prueba; también pasaría con una página vacía.
- **Fix:** Comprobar los identificadores exactos de la primera página y las siguientes, incluido el tamaño máximo.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Faltan pruebas efectivas del orden y de las facturas

- **Location:** [test/orders.test.js:7](repo/test/orders.test.js:7)
- **Problem:** La prueba de pedidos solo comprueba la cantidad y no hay pruebas de la ruta de facturas.
- **Why it fails / scenario:** Un orden incorrecto o el acceso a rutas fuera del directorio de facturas no harían fallar la suite.
- **Fix:** Comprobar el orden de más reciente a más antiguo y probar tanto la descarga válida como el rechazo de recorridos de directorios.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Eliminar la salida de depuración

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Cada llamada a la paginación escribe una línea de depuración.
- **Why it fails / scenario:** Las peticiones normales de pedidos generan salida `DEBUG` innecesaria.
- **Fix:** Eliminar el `console.log`.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 TODO sin referencia de seguimiento

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** El nuevo TODO no referencia una tarea.
- **Why it fails / scenario:** La propuesta de caché queda sin una referencia para su seguimiento.
- **Fix:** Eliminarlo o enlazarlo a una tarea.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- [test/orders.test.js:18](repo/test/orders.test.js:18) comprueba entradas inválidas, ausentes y válidas del parser de enteros positivos.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → pasó; Node informó de un archivo de pruebas y ningún fallo.
- Semgrep: no se pudo ejecutar porque el entorno no dispone de un directorio temporal escribible.
- Callers: 2 contratos cambiados y 3 llamadas fuera del diff revisadas; consumidores externos o dinámicos no comprobados.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=3 required=3 uncertain=0