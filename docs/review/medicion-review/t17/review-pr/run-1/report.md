<!-- review-kit:review-pr -->
## Summary and verdict

La rama añade paginación a `/orders` y descarga de facturas, pero omite la primera página, altera un consumidor existente y permite leer archivos fuera del directorio de facturas. **Nivel 2:** toca `src/invoices.js` y `src/server.js`, identificados como rutas de alto riesgo. Sensitive area: requires human review by an owner.

**Verdict:** CHANGES NEEDED  
**Findings:** Critical 3 · Required 4 · Optional 0 · Nits 0

## Critical

#### C1 La descarga de facturas permite leer archivos del servidor

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** El parámetro `file` de la petición se incorpora a la ruta sin comprobar que permanezca dentro del directorio de facturas.
- **Why it fails / scenario:** Cualquier cliente puede solicitar `/invoices?file=../../package.json` y recibir ese archivo; también puede acceder a otros archivos legibles por el proceso.
- **Fix:** Restringir los nombres admitidos y comprobar que la ruta real, incluidos posibles enlaces simbólicos, permanezca bajo el directorio de facturas. Añadir pruebas de recorrido de directorios.
- **Confidence:** high
- **Source:** security-auditor, code-reviewer

#### C2 La primera página omite los pedidos más recientes

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** El desplazamiento trata el número de página como si empezara en cero, aunque la interfaz empieza en uno.
- **Why it fails / scenario:** `/orders?page=1&size=10` devuelve los IDs 15 a 6 y omite los IDs 25 a 16.
- **Fix:** Calcular `(page - 1) * pageSize` y comprobar en las pruebas el contenido y los totales exactos de las páginas.
- **Confidence:** high
- **Source:** code-reviewer, test-engineer

#### C3 El cambio de orden rompe la selección del pedido más antiguo

- **Location:** [src/orders.js:16](repo/src/orders.js:16)
- **Problem:** `firstOrder()` en `src/stats.js` sigue tomando el primer elemento de `listOrders()`, cuyo orden se ha invertido.
- **Why it fails / scenario:** La función devuelve ahora el pedido 25 en lugar del pedido 1, aunque su contrato es devolver el más antiguo.
- **Fix:** Adaptar `firstOrder()` al nuevo orden y cubrir su comportamiento con una prueba.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 Falta cobertura de la ruta de facturas

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** La nueva ruta no tiene pruebas de integración.
- **Why it fails / scenario:** Una regresión que impida descargar la factura existente o que gestione mal un archivo ausente pasaría la suite actual.
- **Fix:** Probar la respuesta y el contenido de una factura existente y la respuesta 404 para una inexistente.
- **Confidence:** high
- **Source:** test-engineer

#### R2 La prueba de `listOrders` no comprueba el nuevo orden

- **Location:** [test/orders.test.js:7](repo/test/orders.test.js:7)
- **Problem:** La prueba solo comprueba la cantidad de pedidos.
- **Why it fails / scenario:** Si se eliminara la inversión y los pedidos volvieran a aparecer del más antiguo al más reciente, la prueba seguiría pasando.
- **Fix:** Comprobar el orden de los IDs devueltos.
- **Confidence:** high
- **Source:** test-engineer

#### R3 El cálculo del total duplica una función existente

- **Location:** [src/orders.js:25](repo/src/orders.js:25)
- **Problem:** `pageTotal` duplica el cálculo de `sumTotals` en `src/stats.js`.
- **Why it fails / scenario:** Dos implementaciones del mismo cálculo tendrían que mantenerse sincronizadas ante cambios posteriores.
- **Fix:** Compartir una función de suma sin introducir una dependencia circular.
- **Confidence:** high
- **Source:** code-reviewer

#### R4 Queda una salida de depuración en cada petición de pedidos

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** `pageOrders` escribe un mensaje `DEBUG` en cada llamada.
- **Why it fails / scenario:** Cada petición a `/orders` produce salida de depuración en los registros del servicio.
- **Fix:** Eliminar la llamada a `console.log`.
- **Confidence:** high
- **Source:** code-reviewer

<details><summary>Optional, Nits, what's done well and verification</summary>

## Optional

None.

## Nits

None.

## What's done well

- [src/orders.js:31](repo/src/orders.js:31) limita el tamaño de página solicitado a 50.
- [src/server.js:22](repo/src/server.js:22) devuelve un 404 genérico ante errores de lectura, sin exponer los detalles del sistema de archivos.

## Verification

- Comando de verificación indicado en `AGENTS.md`: `npm test` → pasa, sin fallos.
- Semgrep: omitido; no pudo crear un directorio temporal en el entorno de solo lectura y no había una herramienta alternativa disponible.
- Hallazgos refutados por el verificador: 0.
- Hallazgos Optional/Nit descartados por límite: 0.
- No se encontró una carpeta de cambio asociada a la rama.

</details>

REVIEW_RESULT: CHANGES tier=2 critical=3 required=4 uncertain=0