# NOTES.md — K119 第 1 章「Claude Code 的一天」快速演練紀錄

> 快速 demo 模式：主 Claude 直接寫檔，未經 code-writer / QA / reviewer 三 agent 流程。

## 做了什麼

| 步驟 | 產出 | 說明 |
| --- | --- | --- |
| 0. 建專案 | `package.json`、`src/**` | 最小 Express 4 專案：`src/users`、`src/orders`（各有 routes + service）、`src/shared/routes.js` 集中掛路由；`express` 裝在專案內 `node_modules/` |
| 1. 探索 | `MAP.md` | 架構、慣用模式、副作用現況、通知系統建議放置位置 |
| 2. 只提架構 | `ARCH.md` | 檔案結構 + 每檔摘要 + 設計決策，不含程式碼 |
| 3. 實作 | `src/shared/events.js`、`src/notifications/`（`index.js`、`templates.js`、`channels/console.channel.js`）、`scripts/smoke-test.js` | 事件匯流排 + console 管道；users / orders service 各加一行 emit，`app.js` 註冊訂閱 |
| 4. 審查 | `REVIEW.md` | tech lead 視角：4 項上線前必改、5 項建議改 |

## 驗證結果

`npm run smoke`（Node v24.19.0）：

```
[notify:console] to=alice@example.com | 歡迎加入！ | Alice 您好，您的帳號已建立。
[users] 新使用者建立：alice@example.com
[notify:console] to=alice@example.com | 訂單 #1 已成立 | Alice 您好，您的訂單金額為 200。
[orders] 新訂單 #1，金額 200
[orders] 新訂單 #2，金額 5
[notify] order.created 通知失敗：SMTP down
✅ 冒煙測試通過
```

涵蓋：建使用者 → 歡迎通知、建訂單 → 訂單通知、400 錯誤不發通知、管道丟錯時建單仍成功。

## 和書上做法的差異

| 書上 | 本次 |
| --- | --- |
| 在既有的真實專案上跑一天的流程 | 先自己生一個最小 Express 專案當練習標的，所以「探索」的意外發現較少 |
| 每一步是一次對話提示，人看完再下一步（含 Plan mode 討論架構） | 全自動一次跑完，所有選擇採用 Claude 自己的建議，沒有人工把關 |
| 通知接 SendGrid 寄真信 | 只做 console 管道；SendGrid 留作可替換的 channel（介面相同） |
| 審查後開 PR | 不開 PR、不 push、不建 repo，只在本機 commit |
| 測試可能用 Jest 等框架 | 只寫一支無依賴的冒煙測試腳本（`assert` + 內建 `fetch`） |
| 審查通常會請另一個 session / reviewer 做 | 由同一個 session 扮演 tech lead，有「自己審自己」的盲點風險 |

## 已知沒處理的風險

見 `REVIEW.md` 🔴 區：`sentLog` 無上限、log 含 email、無重試 / 佇列、emit 時機在接資料庫後需調整。
