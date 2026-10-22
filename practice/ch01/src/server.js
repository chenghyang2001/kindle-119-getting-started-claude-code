const { createApp } = require('./app');

const PORT = Number(process.env.PORT ?? 3000);
createApp().listen(PORT, () => console.log(`伺服器啟動於 http://localhost:${PORT}`));
