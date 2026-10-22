// 冒煙測試：起 app → 建使用者、建訂單 → 檢查 HTTP 結果與通知紀錄 → 測管道失敗不影響主流程
const assert = require('assert');
const { createApp } = require('../src/app');
const { registerNotifications, getSentLog } = require('../src/notifications');

async function post(base, path, body) {
  const res = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return { status: res.status, json: await res.json() };
}

const tick = () => new Promise((r) => setImmediate(r));

async function run(base) {
  const user = await post(base, '/users', { name: 'Alice', email: 'alice@example.com' });
  assert.strictEqual(user.status, 201, '建立使用者應回 201');

  const order = await post(base, '/orders', { userId: user.json.id, items: [{ price: 100, qty: 2 }] });
  assert.strictEqual(order.status, 201, '建立訂單應回 201');
  await tick();

  const log = getSentLog();
  assert.strictEqual(log.length, 2, `應有 2 筆通知，實際 ${log.length}`);
  assert.strictEqual(log[1].message.subject, `訂單 #${order.json.id} 已成立`);
  assert.strictEqual(log[1].message.to, 'alice@example.com');

  const bad = await post(base, '/orders', { userId: 999, items: [{ price: 1 }] });
  assert.strictEqual(bad.status, 400, '不存在的 userId 應回 400');
  await tick();
  assert.strictEqual(getSentLog().length, 2, '失敗的請求不應發通知');

  // 邊界：管道丟錯時，建單仍要成功
  registerNotifications({ channel: { send: async () => { throw new Error('SMTP down'); } } });
  const order2 = await post(base, '/orders', { userId: user.json.id, items: [{ price: 5 }] });
  assert.strictEqual(order2.status, 201, '通知失敗不應影響建單');
  await tick();
  assert.strictEqual(getSentLog().at(-1).error, 'SMTP down');
}

async function main() {
  const server = createApp().listen(0);
  const base = `http://localhost:${server.address().port}`;
  try {
    await run(base);
    console.log('✅ 冒煙測試通過');
  } catch (err) {
    console.error(`❌ 冒煙測試失敗：${err.message}`);
    process.exitCode = 1;
  } finally {
    server.close();
  }
}

main();
