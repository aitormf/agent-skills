'use strict';

const http = require('node:http');
const { listOrders } = require('./orders');

function handler(req, res) {
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname === '/orders') {
    res.setHeader('content-type', 'application/json');
    return res.end(JSON.stringify(listOrders()));
  }
  res.statusCode = 404;
  res.end('not found');
}

if (require.main === module) {
  http.createServer(handler).listen(3000);
}

module.exports = { handler };
