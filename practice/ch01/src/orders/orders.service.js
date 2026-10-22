const usersService = require('../users/users.service');
const { bus, EVENTS } = require('../shared/events');

const orders = new Map();
let nextId = 1;

function createOrder({ userId, items }) {
  if (usersService.getUser(userId) === null) {
    const err = new Error('userId 不存在');
    err.status = 400;
    throw err;
  }
  if (!Array.isArray(items) || items.length === 0) {
    const err = new Error('items 必須是非空陣列');
    err.status = 400;
    throw err;
  }
  const total = items.reduce((sum, i) => sum + Number(i.price ?? 0) * Number(i.qty ?? 1), 0);
  const order = { id: nextId++, userId: Number(userId), items, total, status: 'created' };
  orders.set(order.id, order);
  bus.emit(EVENTS.ORDER_CREATED, { order, user: usersService.getUser(userId) });
  return order;
}

function getOrder(id) {
  return orders.get(Number(id)) ?? null;
}

function listOrders() {
  return [...orders.values()];
}

module.exports = { createOrder, getOrder, listOrders };
