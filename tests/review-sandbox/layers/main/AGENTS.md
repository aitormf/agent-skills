# orders-service

Servicio HTTP mínimo de pedidos (Node 24, sin dependencias).

## Commands
- Tests: `npm test`
- Arrancar en local: `npm start`

## Code review
- Rama base: `main`
- Rutas de alto riesgo: `src/invoices.js`, `src/server.js` (exponen ficheros del disco)
- Marcar siempre: cualquier lectura de disco construida con datos de la request
