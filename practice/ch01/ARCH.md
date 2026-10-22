# ARCH.md — 通知系統架構提案（步驟 2：只提架構，不寫程式）

## 目標

使用者建立、訂單建立時發出通知。第一版只輸出到 console；之後可替換成 SendGrid 等 email 管道而不動業務模組。

## 檔案結構

```
src/
├── shared/
│   ├── routes.js                 （不變）
│   └── events.js                 ＊新增
├── notifications/                ＊新增
│   ├── index.js                  ＊新增
│   ├── templates.js              ＊新增
│   └── channels/
│       └── console.channel.js    ＊新增
├── users/users.service.js        ～修改：createUser 後 emit 'user.created'
├── orders/orders.service.js      ～修改：createOrder 後 emit 'order.created'
└── app.js                        ～修改：createApp 時呼叫 registerNotifications()
scripts/
└── smoke-test.js                 ＊新增：冒煙測試
```

## 每檔摘要

| 檔案 | 職責 | 對外介面 |
| --- | --- | --- |
| `shared/events.js` | 全域單例 `EventEmitter`，作為領域事件匯流排；集中定義事件名稱常數 | `bus`、`EVENTS = { USER_CREATED, ORDER_CREATED }` |
| `notifications/templates.js` | 把事件 payload 轉成 `{ to, subject, body }` 訊息；純函式、好測 | `buildMessage(eventName, payload)` → 訊息或 `null` |
| `notifications/channels/console.channel.js` | 一個「管道」實作：把訊息印到 console，回傳寄送結果 | `send(message)` → `{ ok, channel }` |
| `notifications/index.js` | 訂閱事件 → 套模板 → 交給管道；錯誤在此吞掉並記錄，不影響主流程；可注入管道（測試 / 未來換 SendGrid） | `registerNotifications({ channel })`、`unregisterNotifications()`、`getSentLog()` |
| `users/users.service.js` | 建立成功後 `bus.emit(USER_CREATED, user)` | 不變 |
| `orders/orders.service.js` | 建立成功後 `bus.emit(ORDER_CREATED, { order, user })` | 不變 |
| `app.js` | `createApp()` 內呼叫 `registerNotifications()`（重複呼叫要冪等） | 不變 |
| `scripts/smoke-test.js` | 起 app（隨機 port）→ POST /users、POST /orders → 確認通知紀錄筆數與內容 → 關閉 | `npm run smoke` |

## 設計決策

1. **事件而非直接呼叫**：業務模組不 require notifications，依賴方向是 notifications → shared，users/orders → shared。
2. **管道可替換**：`channel` 只需實作 `send(message)`；SendGrid 版本只要新增 `channels/sendgrid.channel.js` 並在 `registerNotifications` 傳入。
3. **失敗隔離**：EventEmitter 的 listener 是同步執行，listener 丟錯會讓 `emit` 拋錯 → 必須在 listener 內 try/catch；非同步管道需 `.catch`。
4. **冪等註冊**：`createApp()` 可能被測試多次呼叫，`registerNotifications` 先移除舊 listener 再註冊。

## 不在本次範圍

- SendGrid / 真實寄信、重試、佇列（BullMQ 等）
- 使用者通知偏好（退訂）
- 持久化通知紀錄
