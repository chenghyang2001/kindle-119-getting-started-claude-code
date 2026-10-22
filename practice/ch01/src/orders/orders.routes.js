const express = require('express');
const service = require('./orders.service');

const router = express.Router();

router.get('/', (req, res) => res.json(service.listOrders()));

router.get('/:id', (req, res) => {
  const order = service.getOrder(req.params.id);
  if (order === null) return res.status(404).json({ error: '找不到訂單' });
  return res.json(order);
});

router.post('/', (req, res, next) => {
  try {
    const order = service.createOrder(req.body ?? {});
    // 副作用（目前只有 log）直接寫在 route handler 裡
    console.log(`[orders] 新訂單 #${order.id}，金額 ${order.total}`);
    res.status(201).json(order);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
