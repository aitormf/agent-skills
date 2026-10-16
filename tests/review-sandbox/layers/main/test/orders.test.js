'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { listOrders } = require('../src/orders');

test('listOrders returns all 25 orders', () => {
  assert.equal(listOrders().length, 25);
});
