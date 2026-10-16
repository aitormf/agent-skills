'use strict';

const ORDERS = Array.from({ length: 25 }, (_, i) => ({
  id: i + 1,
  customer: `customer-${(i % 5) + 1}`,
  total: 10 * (i + 1),
}));

const DEFAULT_PAGE_SIZE = 10;
const MAX_PAGE_SIZE = 50;

function listOrders() {
  return ORDERS;
}

function parsePositiveInt(value, fallback) {
  if (value == null) return fallback;
  const n = Number(value);
  return Number.isInteger(n) && n > 0 ? n : fallback;
}

// Pages are 1-indexed: page=1 is the first page.
function pageOrders(orders, page, size) {
  const pageSize = Math.min(size, MAX_PAGE_SIZE);
  const start = page * pageSize;
  console.log('DEBUG pageOrders', { page, pageSize, start });
  return {
    items: orders.slice(start, start + pageSize),
    page,
    pageSize,
    total: orders.length,
  };
}

module.exports = { listOrders, pageOrders, parsePositiveInt, ORDERS, DEFAULT_PAGE_SIZE };
