'use strict';

const { listOrders } = require('./orders');

// First order ever placed (the oldest one): the customer dashboard shows it as "customer since".
function firstOrder() {
  return listOrders()[0];
}

function revenue() {
  return listOrders().reduce((sum, order) => sum + order.total, 0);
}

module.exports = { firstOrder, revenue };
