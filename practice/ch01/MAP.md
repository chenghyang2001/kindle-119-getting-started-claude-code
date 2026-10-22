# MAP.md — 程式碼地圖（步驟 1：探索）

> 對應書上「先請 Claude 探索 codebase，再動手」的流程。本檔只描述現況，不提改動。

## 1. 架構總覽

```
src/
├── server.js            # 進入點：讀 PORT、listen
├── app.js               # createApp()：express.json、/health、掛路由、統一錯誤處理
├── shared/
│   └── routes.js        # registerRoutes(app)：/users、/orders 集中掛載
├── users/
│   ├── users.routes.js  # GET / 、GET /:id、POST /
│   └── users.service.js # 記憶體 Map 存取 + 輸入驗證
└── orders/
    ├── orders.routes.js # GET / 、GET /:id、POST /
    └── orders.service.js# 建單、計算 total；依賴 users.service 驗證 userId
```

請求流向：`server.js → app.js → shared/routes.js → <module>.routes.js → <module>.service.js`

## 2. 慣用模式

| 模式 | 說明 |
| --- | --- |
| 依功能分模組 | 每個業務領域一個資料夾，內含 `*.routes.js` + `*.service.js` |
| routes / service 分層 | routes 只處理 HTTP（狀態碼、req/res）；service 處理驗證與資料 |
| 錯誤傳遞 | service 丟 `Error` 並設 `err.status`；routes 用 `next(err)`；`app.js` 統一轉成 JSON |
| 404 慣例 | service 查無回傳 `null`，routes 回 404 |
| 工廠函式 | `createApp()` 不直接 listen，方便測試時注入 |
| CommonJS | `require` / `module.exports`，無建置步驟 |

## 3. 副作用（side effects）怎麼處理

- 目前唯一的副作用是 **`console.log`**，直接寫在 `users.routes.js` / `orders.routes.js` 的 POST handler 中（建立成功後）。
- 沒有事件機制、沒有佇列、沒有外部服務呼叫。
- 跨模組依賴是**直接 require**：`orders.service` → `users.service.getUser`。
- 資料存在記憶體 `Map`，重啟即清空。

## 4. 通知系統該放哪

**建議：新增 `src/notifications/` 模組，透過 `src/shared/events.js` 的事件匯流排訂閱領域事件。**

理由：

1. 現有結構是「一個業務領域一個資料夾」，通知是獨立關注點，符合同一模式。
2. 若直接在 users / orders 的 route 裡呼叫寄信，會讓業務模組認識通知細節（耦合），之後換 SendGrid 要改多處。
3. 用事件（`user.created`、`order.created`）讓業務模組只「宣告發生了什麼」，通知模組決定「要不要、怎麼通知」。
4. 事件由 **service 層**發出（而非 routes），這樣未來非 HTTP 入口（批次、CLI）建立資料也會觸發通知。
5. 通知寄送失敗**不可**讓主流程失敗（建單成功就是成功），需在通知模組內 try/catch。

需要動到的既有檔案：`users.service.js`、`orders.service.js`（各加一行 emit）、`app.js`（啟動時註冊通知訂閱）。
