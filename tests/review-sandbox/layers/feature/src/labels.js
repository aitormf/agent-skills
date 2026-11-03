'use strict';

function orderLabel(order) {
  if (order.total >= 200) {
    if (order.customer === 'customer-1') return 'vip-large';
    return 'large';
  }
  if (order.total >= 100) {
    if (order.customer === 'customer-1') return 'vip-medium';
    return 'medium';
  }
  if (order.total >= 50) {
    if (order.customer === 'customer-1') return 'vip-small';
    return 'small';
  }
  if (order.customer === 'customer-1') return 'vip-tiny';
  return 'tiny';
}

module.exports = { orderLabel };
