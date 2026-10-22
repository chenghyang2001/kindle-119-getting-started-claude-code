# NOTES：K119 第 3 章演練紀錄

> 快速 demo 模式：未經 QA／code-reviewer 審查，只求看懂流程。

## 做了什麼

| commit | 內容 |
| --- | --- |
| `ff52a17` | 建 TypeScript＋Jest 專案（套件裝在專案內），放入重構前的 `processOrder`（巢狀 6 層、驗證與業務混在一起）與 7 個既有測試 |
| `3cd15db` | 步驟 1：只寫 `PLAN.md`，不改程式 |
| `d89615d` | 步驟 2：只重構驗證 → `src/validation.ts` 抽出 `checkOrderExists` / `checkCustomerId` / `checkHasItems` / `checkItems` / `calculateTotal` / `checkTotalWithinLimit` / `validateOrder`；`processOrder` 改成 early return |
| `398cccc` | 步驟 3：`Db` 介面加 `transaction(fn)`，假 db 用快照實作回滾；`processOrder` 把兩個寫入包進交易；新增 2 個交易測試 |
| （本次） | `PROMPTS.md`、`NOTES.md` |

檔案結構：

```text
src/db.ts            Db / DbWriter / Order 型別（含 transaction）
src/validation.ts    具名驗證函式
src/processOrder.ts  先驗證、再用交易寫入
tests/fakeDb.ts      記憶體假 db（快照式回滾、可指定某商品扣庫存失敗）
tests/processOrder.test.ts
```

## 驗證結果

| 時間點 | `npm test` | `tsc --noEmit` |
| --- | --- | --- |
| 重構前 | 7 / 7 通過 | — |
| 步驟 2 後 | 7 / 7 通過（測試完全沒改） | 通過 |
| 步驟 3 後 | 9 / 9 通過 | 通過 |

**反向驗證**：把 `processOrder.ts` 暫時換回步驟 2（沒有交易）的版本，
新增的 2 個交易測試會失敗（`2 failed, 7 passed`），證明回滾測試真的有在把關；驗證完已還原。

## 和書上做法的差異

1. **計畫的確認者**：書上是「Claude 寫計畫 → 人看過 → 才動手」。這次是全自動，計畫寫完由我自己照著做，沒有人工審核那一關。
2. **計畫有抓到一個陷阱**：原程式是逐項「先查數量、再查價格」。若照直覺拆成「checkQuantities」「checkPrices」兩個函式，
   同時有兩種錯誤的訂單會回傳不同錯誤訊息。因此合併成 `checkItems` 保留原順序 —— 這正是「先要計畫」的價值。
   但既有測試沒有覆蓋這種「雙重錯誤」的情境，所以這個行為目前只靠程式碼維持，沒有測試保護。
3. **交易是假的**：書上情境是真資料庫交易；這裡用假 db 在交易開始時做快照、失敗時還原，只能示範概念，不涵蓋並行、隔離等級等真 DB 問題。
4. **新增的對外行為**：寫入失敗時回傳 `{ ok: false, error: "寫入失敗，已回滾" }`，原本是直接把例外丟出去。這是刻意的行為改變，已寫進測試。
5. **環境踩坑**：`npm install typescript` 預設裝到 TypeScript 7，ts-jest 不支援（缺 JS compiler API），改裝 `typescript@5`（5.9.3）才能跑。

## 已知未處理的風險

- 「雙重錯誤」的錯誤優先順序沒有測試保護（見差異 2）。
- 金額上限邊界（剛好 100000）沒有專門測試。
- `processOrder` 在寫入失敗時用 `console.error` 記錄，沒有正式 logger。
