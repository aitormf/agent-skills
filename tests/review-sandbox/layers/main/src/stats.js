'use strict';

const { listOrders, orderLabel } = require('./orders');

// First order ever placed (the oldest one): the customer dashboard shows it as "customer since".
function firstOrder() {
  return listOrders()[0];
}

function sumTotals(orders) {
  return orders.reduce((sum, order) => sum + order.total, 0);
}

function revenue() {
  return sumTotals(listOrders());
}

function labelCounts() {
  const counts = {};
  for (const order of listOrders()) {
    const label = orderLabel(order);
    counts[label] = (counts[label] || 0) + 1;
  }
  return counts;
}

module.exports = { firstOrder, revenue, sumTotals, labelCounts };
