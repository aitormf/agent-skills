# Sandbox — hallazgos esperados

Este fichero queda **fuera** del repo generado (`repo/`) para no dar pistas al revisor.
Sirve para puntuar la salida de `/review-prepush` y `/review-pr`.

Tarea declarada en el commit de la rama `feature/orders-pagination-invoices`:
"Añadir paginación a /orders y endpoint /invoices para descargar facturas".

## Bugs plantados (deben aparecer)

| # | Tipo | Dónde | Qué | Severidad esperada |
|---|------|-------|-----|--------------------|
| B1 | Lógica | `src/orders.js` (`pageOrders`) | `start = page * pageSize` con páginas 1-indexadas: `page=1` devuelve los pedidos 11–20 y se salta el primer bloque; la última página sale vacía. Corrección: `(page - 1) * pageSize`. | Critical |
| B2 | Test inútil | `test/orders.test.js` ("pageOrders returns a page of orders") | Solo comprueba que `items` es un array de ≤10 elementos y el total; pasa con B1. Debería comprobar los ids concretos de la página 1 (1–10) y la última página. | Required |
| B3 | Seguridad | `src/invoices.js` (`readInvoice`) + `src/server.js` (`/invoices`) | Path traversal: `?file=../../package.json` (o `../../../../etc/passwd`) lee cualquier fichero accesible. Corrección: validar `file` contra un patrón (`^[\w-]+\.pdf$`) y/o comprobar que `path.resolve` queda dentro de `INVOICES_DIR`. | Critical |
| B4 | Restos | `src/orders.js` | `console.log('DEBUG pageOrders', …)` en cada petición. | Required (o Optional) |
| B5 | Restos | `src/invoices.js` | `// TODO: cache invoices in memory` sin ticket. | Nit / Optional |

## Señuelos (NO deberían sobrevivir como hallazgos)

| # | Dónde | Por qué parece un bug | Por qué no lo es |
|---|-------|-----------------------|------------------|
| D1 | `parsePositiveInt`: `value == null` | Igualdad no estricta | Idiomático: cubre `null` y `undefined` a la vez, intencionado. |
| D2 | `orders.slice(start, start + pageSize)` | "off-by-one en el final" | `slice` tiene fin exclusivo; devuelve exactamente `pageSize` elementos. |
| D3 | `Math.min(size, MAX_PAGE_SIZE)` | "no valida size" | `size` ya llega validado como entero positivo por `parsePositiveInt`. |

## Discutible (aceptable en cualquier sentido)

- `catch {}` en `/invoices` que devuelve 404 para cualquier error: aceptable como Optional ("distinguir ENOENT de otros errores").
- Falta de test para `/invoices`: aceptable como Required/Optional, sobre todo junto a B3.
