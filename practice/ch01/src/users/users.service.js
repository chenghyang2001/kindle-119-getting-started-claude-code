const { bus, EVENTS } = require('../shared/events');

// 記憶體內的使用者資料（demo 用，重啟即清空）
const users = new Map();
let nextId = 1;

function createUser({ name, email }) {
  if (!name || !email) {
    const err = new Error('name 與 email 為必填');
    err.status = 400;
    throw err;
  }
  const user = { id: nextId++, name, email, createdAt: new Date().toISOString() };
  users.set(user.id, user);
  bus.emit(EVENTS.USER_CREATED, user);
  return user;
}

function getUser(id) {
  return users.get(Number(id)) ?? null;
}

function listUsers() {
  return [...users.values()];
}

module.exports = { createUser, getUser, listUsers };
