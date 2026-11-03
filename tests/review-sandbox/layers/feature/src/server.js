'use strict';

const http = require('node:http');
const { listOrders, pageOrders, parsePositiveInt, DEFAULT_PAGE_SIZE } = require('./orders');
const { readInvoice } = require('./invoices');

function handler(req, res) {
  const url = new URL(req.url, 'http://localhost');

  if (url.pathname === '/orders') {
    const page = parsePositiveInt(url.searchParams.get('page'), 1);
    const size = parsePositiveInt(url.searchParams.get('size'), DEFAULT_PAGE_SIZE);
    res.setHeader('content-type', 'application/json');
    return res.end(JSON.stringify(pageOrders(listOrders(), page, size)));
  }

  if (url.pathname === '/invoices') {
    try {
      const pdf = readInvoice(url.searchParams.get('file'));
      res.setHeader('content-type', 'application/pdf');
      return res.end(pdf);
    } catch {
      res.statusCode = 404;
      return res.end('invoice not found');
    }
  }

  res.statusCode = 404;
  res.end('not found');
}

if (require.main === module) {
  http.createServer(handler).listen(3000);
}

module.exports = { handler };
