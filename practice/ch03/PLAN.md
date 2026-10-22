# PLAN：processOrder 重構計畫

> 這一步只寫計畫，不改任何程式碼。

## 現況問題

- `src/processOrder.ts` 巢狀 6 層 if/else，錯誤訊息離對應的條件很遠，難讀。
- 驗證（客戶、商品、數量、價格、金額上限）和業務邏輯（算總額、寫 db）混在同一個函式。
- 兩個 db 寫入（`insertOrder`、`decrementStock`）沒有交易保護：扣庫存失敗時，訂單已經寫進去，資料會不一致。

## 目標

1. 讓驗證規則一條一條看得懂、可以單獨測。
2. 讓 db 寫入要嘛全成功、要嘛全回滾。
3. 對外行為不變：回傳格式 `{ ok, orderId?, error? }` 與錯誤訊息文字不變。

## 限制

- 每一步都要讓既有 7 個測試維持通過，才可 commit。
- 一次只做一件事：驗證重構與交易改造分成兩個 commit。
- 不引入新套件；交易用假 db 物件模擬，不接真資料庫。

## 步驟

### 步驟 2：只重構驗證（不碰 db 寫入）

1. 新增 `src/validation.ts`，每個檢查抽成具名函式，回傳 `string | null`（錯誤訊息或通過）：
   - `checkOrderExists`
   - `checkCustomerId`
   - `checkHasItems`
   - `checkItemQuantities`
   - `checkItemPrices`
   - `checkTotalWithinLimit`（另抽 `calculateTotal`）
2. `validateOrder` 依原本的順序跑這些檢查，遇到第一個錯誤就回傳。
3. `processOrder` 改成 guard clause（early return）：驗證失敗 → 直接 return；之後才進業務邏輯。
4. 注意原本的檢查順序：每個商品是「先查數量、再查價格」逐一檢查。若改成「全部數量 → 全部價格」，
   在同時有兩種錯誤的訂單上錯誤訊息可能不同。→ 合併成 `checkItems` 逐項檢查，保留原順序。
5. 跑 `npm test` 通過 → commit。

### 步驟 3：兩個 db 寫入包進交易

1. `Db` 介面加 `transaction(fn)`：fn 拿到交易用的 `tx`，fn 丟錯就回滾。
2. 假 db 實作：交易開始先快照 orders / stock，失敗時還原快照再把錯誤往上丟。
3. `processOrder` 用 `db.transaction(tx => ...)` 包住 `insertOrder` 與 `decrementStock`；
   寫入失敗時回傳 `{ ok: false, error: "寫入失敗，已回滾" }`。
4. 新增測試：讓 `decrementStock` 在第二個商品丟錯 → 斷言回傳失敗、訂單與庫存都還原。
5. 跑 `npm test` 通過 → commit。

## 風險與邊界

| 風險 | 處理 |
| --- | --- |
| 驗證順序改變導致錯誤訊息不同 | 保留逐項「先數量後價格」 |
| 交易內部丟錯被吞掉 | 回滾後重新丟出，由 processOrder 統一轉成錯誤結果 |
| 金額剛好等於上限 100000 | 維持「<= 上限算通過」 |
