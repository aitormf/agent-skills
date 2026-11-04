## Summary and verdict

La rama añade paginación de pedidos y descarga de facturas, pero la revisión confirmó una lectura de archivos fuera del directorio permitido y tres regresiones funcionales. Las pruebas existentes pasan, aunque no detectan esos problemas.

**Verdict:** BLOCK

## Critical

#### C1 Lectura de archivos fuera del directorio de facturas

- **Location:** [src/invoices.js:10](repo/src/invoices.js:10)
- **Problem:** El nombre recibido en la petición se incorpora a la ruta sin comprobar que permanezca dentro del directorio de facturas.
- **Why it fails / scenario:** Un cliente puede solicitar `/invoices?file=../../package.json` y obtener un archivo legible por el proceso.
- **Fix:** Validar los nombres de factura y garantizar que la ruta resuelta, incluidos enlaces simbólicos, permanezca dentro del directorio permitido. Añadir una prueba de traversal.
- **Confidence:** high
- **Source:** code-reviewer

#### C2 La primera página omite los pedidos más recientes

- **Location:** [src/orders.js:32](repo/src/orders.js:32)
- **Problem:** El desplazamiento trata las páginas como si empezaran en cero.
- **Why it fails / scenario:** `/orders?page=1&size=10` devuelve los pedidos 15 a 6 en vez de los pedidos 25 a 16; con `size=50`, la primera página queda vacía.
- **Fix:** Calcular el inicio como `(page - 1) * pageSize` y comprobar el contenido exacto de varias páginas.
- **Confidence:** high
- **Source:** code-reviewer

#### C3 La primera orden histórica pasa a ser la más reciente

- **Location:** [src/stats.js:7](repo/src/stats.js:7)
- **Problem:** El cambio de orden de `listOrders()` rompe `firstOrder()`, que toma el primer elemento como la orden más antigua.
- **Why it fails / scenario:** `firstOrder()` devuelve la orden 25 en lugar de la 1.
- **Fix:** Adaptar `firstOrder()` al nuevo contrato y cubrir el resultado con una prueba.
- **Confidence:** high
- **Source:** code-reviewer

#### C4 La factura incluida no es un PDF válido

- **Location:** [data/invoices/2026-001.pdf:1](repo/data/invoices/2026-001.pdf:1)
- **Problem:** El archivo contiene una línea de texto sin estructura de documento PDF.
- **Why it fails / scenario:** Un cliente que solicita esta factura recibe una respuesta que un lector de PDF no puede abrir.
- **Fix:** Sustituir el archivo por un PDF válido y comprobar que la respuesta entregue un documento utilizable.
- **Confidence:** high
- **Source:** code-reviewer

## Required

#### R1 La prueba de paginación no comprueba el contenido

- **Location:** [test/orders.test.js:11](repo/test/orders.test.js:11)
- **Problem:** La prueba acepta cualquier array de hasta diez elementos, incluso uno vacío.
- **Why it fails / scenario:** La implementación desplaza todas las páginas y aun así supera la prueba.
- **Fix:** Comprobar los identificadores y totales exactos de la primera página, páginas posteriores y tamaño máximo, incluyendo la ruta HTTP.
- **Confidence:** high
- **Source:** code-reviewer

#### R2 Falta cobertura para facturas y el nuevo orden

- **Location:** [src/server.js:17](repo/src/server.js:17)
- **Problem:** No hay pruebas de la nueva ruta de facturas ni una aserción que compruebe el orden de `listOrders()`.
- **Why it fails / scenario:** Un endpoint que siempre devolviera 404, un traversal de rutas o una lista en el orden anterior pasarían las pruebas existentes.
- **Fix:** Añadir pruebas para una factura válida, archivo ausente, traversal y orden exacto de los pedidos.
- **Confidence:** high
- **Source:** code-reviewer

#### R3 Salida de depuración en cada petición

- **Location:** [src/orders.js:33](repo/src/orders.js:33)
- **Problem:** Se ha dejado un `console.log` de depuración en la paginación.
- **Why it fails / scenario:** Cada consulta de pedidos escribe información de depuración en la salida del servidor.
- **Fix:** Eliminar la salida de depuración.
- **Confidence:** high
- **Source:** code-reviewer

## Optional

None.

## Nits

#### N1 TODO sin referencia

- **Location:** [src/invoices.js:8](repo/src/invoices.js:8)
- **Problem:** El nuevo TODO no identifica una tarea de seguimiento.
- **Why it fails / scenario:** No queda una referencia para seguir la implementación propuesta.
- **Fix:** Eliminarlo o vincularlo a una tarea.
- **Confidence:** high
- **Source:** code-reviewer
- **Impact / cost:** low / S

## What's done well

- La prueba de [test/orders.test.js](repo/test/orders.test.js:18) comprueba explícitamente entradas inválidas y valores por defecto para la conversión de enteros positivos.

## Verification

- Commands found in AGENTS.md: `npm test`.
- Run: `npm test` → pasó; un archivo de pruebas, cero fallos.
- Semgrep: no pudo ejecutarse porque el entorno no dispone de un directorio temporal utilizable; no hay alternativa MCP disponible.
- Callers: se revisaron tres usos externos al diff del símbolo cuyo contrato cambió; ninguno quedó sin comprobar.
- Findings refuted by the verifier: 0.
- Optional/Nit findings dropped by the limit (Max Optional=3, Max Nits=3): 0.

REVIEW_RESULT: BLOCK critical=4 required=3 uncertain=0