# REVIEW.md — Tech Lead 審查（步驟 4）

**審查範圍**：`src/shared/events.js`、`src/notifications/**`、`users.service.js` / `orders.service.js` / `app.js` 的修改、`scripts/smoke-test.js`
**結論**：✅ **以 demo（console 版）而言可以合併**；但接 SendGrid 上線前，下列 🔴 項目必須先處理。

## 做得好的地方

- 依 ARCH.md 落實「事件解耦」：users / orders 不 require notifications，依賴方向正確。
- 事件從 service 層發出，非 HTTP 入口建立資料也會通知。
- 失敗隔離有做且有測：管道丟錯時建單仍回 201（冒煙測試第 4 段）。
- `registerNotifications` 冪等，且管道可注入，換 SendGrid 只需新增一個 channel 檔。
- `templates.js` 是純函式，好寫單元測試。

## 🔴 上線前必改

| # | 位置 | 問題 | 建議 |
| --- | --- | --- | --- |
| 1 | `notifications/index.js` `sentLog` | 模組層陣列無上限成長，正式環境會記憶體洩漏；且它其實只是給測試用的 | 改成只在測試注入 recorder channel，或加上限（ring buffer） |
| 2 | `channels/console.channel.js` | log 直接印出收件人 email（PII），正式環境 log 會外流個資 | 遮罩 email（`a***@example.com`）或只記 user id |
| 3 | 整體 | 沒有重試也沒有持久化；process 在 `send` 進行中重啟，通知就遺失 | 接 SendGrid 時改為佇列（BullMQ / DB outbox），至少加有限次重試 |
| 4 | `*.service.js` emit 時機 | 目前是記憶體 Map 所以沒差；換成資料庫後，若在交易 commit 前 emit，rollback 時會寄出不存在訂單的通知 | 約定「commit 後才 emit」，或用 outbox pattern |

## 🟡 建議改

| # | 位置 | 問題 | 建議 |
| --- | --- | --- | --- |
| 5 | `app.js` | `createApp()` 會改全域狀態（重設通知訂閱），多個 app 實例互相覆蓋；測試必須注意呼叫順序 | 把 `registerNotifications` 移到 `server.js`，或讓 bus 由 `createApp` 建立並注入 |
| 6 | `users.service.js` | emit 傳出的是儲存中的同一物件參照，listener 可改到內部資料 | emit `{ ...user }` 或 `Object.freeze` |
| 7 | `*.routes.js` | 舊的 `console.log` 副作用與通知 log 重複 | 移除或改成統一 logger |
| 8 | `scripts/smoke-test.js` | 用 `setImmediate` 等通知完成；真實網路管道會變慢而 flaky | 讓 `deliver` 回傳 promise 供測試 await，或測試用同步 recorder |
| 9 | 測試 | 只有冒煙測試，`templates.js` 無單元測試 | 加 node:test 單元測試（含未知事件回傳 null） |

## 🟢 既有問題（非本次引入，記錄供參）

- `orders.service.js`：`price` 非數字時 `total` 會變 `NaN`；`email` 沒驗證格式。
- 資料存記憶體，重啟清空。

## 給 PR 作者的一句話

架構方向對，測試有涵蓋最重要的「通知失敗不影響主流程」。console 版先合；下一張票（SendGrid）請把 #1–#4 一起帶上。
