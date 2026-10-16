'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { listOrders, pageOrders, parsePositiveInt, ORDERS } = require('../src/orders');

test('listOrders returns all 25 orders', () => {
  assert.equal(listOrders().length, 25);
});

test('pageOrders returns a page of orders', () => {
  const result = pageOrders(ORDERS, 1, 10);
  assert.ok(Array.isArray(result.items));
  assert.ok(result.items.length <= 10);
  assert.equal(result.total, 25);
});

test('parsePositiveInt falls back on invalid input', () => {
  assert.equal(parsePositiveInt('abc', 1), 1);
  assert.equal(parsePositiveInt('-3', 1), 1);
  assert.equal(parsePositiveInt(null, 7), 7);
  assert.equal(parsePositiveInt('4', 1), 4);
});
