import { createApp } from './app.js';

const port = Number(process.env.PORT ?? 3000);
if (!Number.isInteger(port) || port <= 0) {
  console.error(`錯誤：PORT 必須是正整數，收到 ${process.env.PORT}`);
  process.exit(1);
}

const server = createApp().listen(port, () => {
  console.log(`Inventory API 已啟動：http://localhost:${port}`);
});
server.on('error', (err) => {
  console.error('伺服器啟動失敗：', err.message);
  process.exit(1);
});
