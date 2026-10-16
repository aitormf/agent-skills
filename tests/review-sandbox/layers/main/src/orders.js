'use strict';

const ORDERS = Array.from({ length: 25 }, (_, i) => ({
  id: i + 1,
  customer: `customer-${(i % 5) + 1}`,
  total: 10 * (i + 1),
}));

function listOrders() {
  return ORDERS;
}

module.exports = { listOrders, ORDERS };
