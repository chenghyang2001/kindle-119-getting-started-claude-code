const express = require('express');
const { registerRoutes } = require('./shared/routes');
const { registerNotifications } = require('./notifications');

function createApp() {
  registerNotifications();
  const app = express();
  app.use(express.json());
  app.get('/health', (req, res) => res.json({ ok: true }));
  registerRoutes(app);

  // 統一錯誤處理：有 status 用 status，否則 500 且不洩漏內部訊息
  app.use((err, req, res, next) => {
    const status = err.status ?? 500;
    if (status === 500) console.error('[app] 未預期錯誤：', err);
    res.status(status).json({ error: status === 500 ? '伺服器內部錯誤' : err.message });
  });
  return app;
}

module.exports = { createApp };
