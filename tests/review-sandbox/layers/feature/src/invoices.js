'use strict';

const fs = require('node:fs');
const path = require('node:path');

const INVOICES_DIR = path.join(__dirname, '..', 'data', 'invoices');

// TODO: cache invoices in memory
function readInvoice(name) {
  const file = path.join(INVOICES_DIR, name);
  return fs.readFileSync(file);
}

module.exports = { readInvoice, INVOICES_DIR };
