# 演練筆記：K119 第 9 章「日常實用食譜」

日期：2026-10-22 · 模式：快速 demo 模式（沒有經過 QA／審查 agent）

## 做了什麼

挑了三道食譜，全部做在同一個專案裡：

1. **REST API**（Express 5 + TypeScript）
   - 依 products／categories／movements 三張表設計 API，資料存在記憶體（`src/store.ts`）
   - zod 驗證 body、路徑參數、查詢字串（`src/schemas.ts`）
   - 統一錯誤處理（`src/errors.ts`）：所有錯誤都是 `{ error: { code, message, details? } }`
   - 商業規則：庫存只能透過 movements 改變、出貨不能讓庫存變負數、SKU 和分類名稱不能重複、有關聯資料時不能刪除
   - `tests/api.test.ts` 用 supertest 測 17 個情境
2. **CSV 轉 JSON 腳本**（`src/scripts/csv-to-json.ts`）
   - 自己準備了 `data/export.csv`（10 筆，第 8 行價格是 `not-a-price`）
   - 自己寫了一個小型 CSV 解析器（支援引號、逗號、`""`、CRLF、BOM），每列用 zod 驗證
   - 輸出 `data/products.json`（9 筆），錯誤列印到 stderr，結束碼 2
   - `tests/csv-to-json.test.ts` 測 5 個情境
3. **ESLint + Prettier + .editorconfig**
   - ESLint 扁平設定：`@eslint/js` 建議規則 + `typescript-eslint` 型別檢查規則 + `eslint-config-prettier`
   - Prettier：單引號、尾逗號、行寬 100、LF

最後寫了 `README.md`。

## 驗證結果

| 項目                   | 結果                                                                     |
| ---------------------- | ------------------------------------------------------------------------ |
| `npx tsc --noEmit`     | 通過                                                                     |
| `npm test`             | 2 個測試檔、22 個測試全部通過                                            |
| `npm run lint`         | 第一次 29 個錯誤 → 修完後 0 錯誤 0 警告                                  |
| `npm run format:check` | 全部符合 Prettier                                                        |
| `npm run csv:convert`  | 9 筆成功、第 8 行被略過，結束碼 2                                        |
| 額外測試               | 帶 BOM 的 CSV 可正確解析；找不到輸入檔時印出錯誤、結束碼 1               |
| 實際啟動伺服器         | `PORT=3999` 啟動，用 curl 打 `/health`、建分類、建商品都正常，測完已關閉 |

### 第一次 lint 的 29 個錯誤怎麼處理

- 27 個 `no-unsafe-*`：都在測試檔，因為 supertest 的 `res.body` 型別是 `any`。只在 `tests/**` 關掉這三條規則，正式程式碼仍然維持嚴格。
- 1 個 `no-irregular-whitespace`：寫檔工具把正規表達式裡的 BOM 跳脫序列（U+FEFF）轉成了看不見的真實 BOM 字元，改回跳脫寫法。
- 1 個 `preserve-caught-error`（ESLint 10 新規則）：重新丟出錯誤時補上 `{ cause: err }`。

## 和書上做法的差異

> 這次沒有逐字對照書中程式碼。第一列與最後一列依題目說明確定；其餘幾列是這類食譜的常見做法，標「（推測）」。

| 書上／常見做法                    | 這次                                  | 原因                                                                                |
| --------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------- |
| API 接 PostgreSQL                 | 用記憶體 `Store` 類別                 | 題目要求不接資料庫；`createApp(store)` 可以注入資料層，之後換成資料庫實作不用改路由 |
| Jest + ts-jest（推測）            | Vitest + supertest                    | Vitest 直接支援 TypeScript 和 ESM，不需要額外設定；supertest 用法一樣               |
| 用 `csv-parse` 之類的套件（推測） | 自己寫小型解析器                      | 少一個依賴，也方便說明引號與跳脫怎麼處理；正式專案還是建議用成熟套件                |
| `.eslintrc` 設定檔（推測）        | ESLint 10 扁平設定 `eslint.config.js` | ESLint 9 以後只支援扁平設定                                                         |
| Express 4（推測）                 | Express 5                             | 最新版；同步丟出的錯誤會自動交給錯誤處理 middleware                                 |
| 讓 Claude 一步步產生、逐一確認    | 全自動、不停下來問                    | 這次的指示是全自動完成                                                              |

### TypeScript 版本

安裝到的是 **TypeScript 6.0.3**。typescript-eslint 8.72 支援範圍是 `>=4.8.4 <6.1.0`，6.0.3 在範圍內，tsc、tsx、Vitest、ESLint 都正常，所以**沒有退回 5.x**。

## 已知限制（快速模式沒處理的部分）

- 資料只在記憶體，重啟就消失；也沒有處理多個請求同時改庫存的情況
- 列表沒有分頁
- 沒有身分驗證和存取權限
- CSV 解析器沒有處理超大檔案的串流讀取，整個檔案一次讀進記憶體
- `npm install` 時 esbuild 的 postinstall 被 npm 的 allow-scripts 擋下警告，但 tsx／Vitest 執行正常，沒有另外處理
