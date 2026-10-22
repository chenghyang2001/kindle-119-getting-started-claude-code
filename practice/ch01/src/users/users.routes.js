const express = require('express');
const service = require('./users.service');

const router = express.Router();

router.get('/', (req, res) => res.json(service.listUsers()));

router.get('/:id', (req, res) => {
  const user = service.getUser(req.params.id);
  if (user === null) return res.status(404).json({ error: '找不到使用者' });
  return res.json(user);
});

router.post('/', (req, res, next) => {
  try {
    const user = service.createUser(req.body ?? {});
    // 副作用（目前只有 log）直接寫在 route handler 裡
    console.log(`[users] 新使用者建立：${user.email}`);
    res.status(201).json(user);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
