// 集中掛載各模組的 router，app.js 只需呼叫 registerRoutes(app)
const usersRouter = require('../users/users.routes');
const ordersRouter = require('../orders/orders.routes');

function registerRoutes(app) {
  app.use('/users', usersRouter);
  app.use('/orders', ordersRouter);
}

module.exports = { registerRoutes };
