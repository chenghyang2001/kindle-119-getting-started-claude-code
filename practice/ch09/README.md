# K119 Ch09 Inventory

用 Express 5 + TypeScript 做的小型庫存管理 REST API，附 CSV 轉 JSON 工具與 ESLint／Prettier 設定。
這是《Getting Started with Claude Code》第 9 章「日常實用食譜」的練習專案。

- **REST API**：商品（products）、分類（categories）、庫存異動（movements），用 zod 驗證輸入，所有錯誤都回同一種格式
- **CSV 轉換**：把 `data/export.csv` 轉成 `data/products.json`，格式錯誤的列會略過並回報
- **程式碼品質**：ESLint（含型別檢查規則）＋ Prettier ＋ `.editorconfig`

> 資料存在記憶體裡，伺服器重啟就清空。這是刻意的簡化，沒有接 PostgreSQL。

## 需求

- Node.js 20 以上（開發時用 24.19）
- npm

## 快速開始

```bash
npm install
npm run dev          # 開發模式（檔案變更自動重啟），預設 http://localhost:3000
npm test             # 執行全部測試
```

改用其他 port：`PORT=4000 npm start`。

## 指令

| 指令                   | 用途                                              |
| ---------------------- | ------------------------------------------------- |
| `npm run dev`          | 用 tsx watch 啟動 API                             |
| `npm start`            | 啟動 API（不監看檔案）                            |
| `npm test`             | Vitest + supertest 測試（22 個）                  |
| `npm run typecheck`    | `tsc --noEmit` 型別檢查                           |
| `npm run csv:convert`  | CSV → JSON，可加參數：`-- <輸入.csv> <輸出.json>` |
| `npm run lint`         | ESLint 檢查                                       |
| `npm run lint:fix`     | ESLint 自動修正                                   |
| `npm run format`       | Prettier 格式化全部檔案                           |
| `npm run format:check` | 只檢查格式，不改檔                                |

## API

所有路徑都在 `/api` 底下，請求與回應都是 JSON。成功時資料放在 `data` 欄位。

### 資料模型

| 資源         | 欄位                                                                                                                                   |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `categories` | `id`, `name`（唯一）, `description?`                                                                                                   |
| `products`   | `id`, `sku`（唯一，大寫英數與 `-`，3–32 字）, `name`, `categoryId`, `price`（≥ 0，最多兩位小數）, `quantity`, `createdAt`, `updatedAt` |
| `movements`  | `id`, `productId`, `type`（`in` 進貨／`out` 出貨／`adjust` 盤點調整）, `quantity`, `note?`, `createdAt`                                |

### 端點

| 方法     | 路徑                          | 說明                                                         |
| -------- | ----------------------------- | ------------------------------------------------------------ |
| `GET`    | `/health`                     | 健康檢查                                                     |
| `GET`    | `/api/categories`             | 列出分類                                                     |
| `GET`    | `/api/categories/:id`         | 取得分類                                                     |
| `POST`   | `/api/categories`             | 建立分類                                                     |
| `PATCH`  | `/api/categories/:id`         | 更新分類                                                     |
| `DELETE` | `/api/categories/:id`         | 刪除分類（底下還有商品時回 409）                             |
| `GET`    | `/api/products`               | 列出商品，可用 `?categoryId=` 與 `?q=`（比對名稱或 SKU）篩選 |
| `GET`    | `/api/products/:id`           | 取得商品                                                     |
| `GET`    | `/api/products/:id/movements` | 該商品的異動紀錄                                             |
| `POST`   | `/api/products`               | 建立商品（可給初始 `quantity`）                              |
| `PATCH`  | `/api/products/:id`           | 更新商品；`quantity` 會被忽略                                |
| `DELETE` | `/api/products/:id`           | 刪除商品（有異動紀錄時回 409）                               |
| `GET`    | `/api/movements`              | 列出異動，可用 `?productId=` 篩選                            |
| `POST`   | `/api/movements`              | 新增異動並更新庫存；回應含更新後的 `product`                 |

### 庫存規則

- 庫存數量只能透過 `POST /api/movements` 改變，`PATCH` 商品時不能直接改數量，這樣每次變動都有紀錄。
- `in`、`out` 的數量必須是正整數；`adjust` 可正可負，但不能是 0。
- 出貨或調整後庫存小於 0 時回 `409 INSUFFICIENT_STOCK`，庫存不會變動。

### 範例

```bash
curl -X POST localhost:3000/api/categories -H 'Content-Type: application/json' \
  -d '{"name":"文具"}'

curl -X POST localhost:3000/api/products -H 'Content-Type: application/json' \
  -d '{"sku":"PEN-001","name":"藍色原子筆","categoryId":1,"price":15,"quantity":10}'

curl -X POST localhost:3000/api/movements -H 'Content-Type: application/json' \
  -d '{"productId":1,"type":"out","quantity":3,"note":"門市出貨"}'
```

### 錯誤格式

所有錯誤都回同一種結構：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "請求資料驗證失敗",
    "details": [{ "path": "sku", "message": "SKU 只能包含大寫英數與連字號，長度 3–32" }]
  }
}
```

| 狀態 | `code`                                                             | 情況                                 |
| ---- | ------------------------------------------------------------------ | ------------------------------------ |
| 400  | `VALIDATION_ERROR`                                                 | zod 驗證失敗，`details` 列出每個欄位 |
| 400  | `INVALID_JSON`                                                     | 請求內容不是合法 JSON                |
| 400  | `INVALID_QUANTITY`                                                 | `in`／`out` 給了負數                 |
| 404  | `NOT_FOUND` / `ROUTE_NOT_FOUND`                                    | 資源或路由不存在                     |
| 409  | `DUPLICATE_SKU` / `DUPLICATE_CATEGORY`                             | 唯一值重複                           |
| 409  | `CATEGORY_IN_USE` / `PRODUCT_HAS_MOVEMENTS` / `INSUFFICIENT_STOCK` | 違反資料一致性                       |
| 500  | `INTERNAL_ERROR`                                                   | 未預期錯誤（不回傳內部細節）         |

## CSV 轉 JSON

```bash
npm run csv:convert                                  # data/export.csv → data/products.json
npm run csv:convert -- input.csv output.json         # 自訂路徑
```

- CSV 需要這些欄位：`sku,name,category,price,quantity,updated_at`
- 支援雙引號欄位、欄位內逗號、`""` 跳脫、CRLF 換行和 UTF-8 BOM（Excel 匯出常見）
- 每一列用 zod 驗證，失敗的列會略過，並在 stderr 印出行號和原因
- 結束碼：`0` 全部成功、`2` 有列被略過、`1` 無法執行（找不到檔案、缺欄位、引號未關閉）

範例檔 `data/export.csv` 有 10 筆，其中第 8 行的 `price` 故意寫成 `not-a-price`：

```text
✔ 已轉換 9 筆 → data/products.json
✘ 略過 1 筆格式錯誤的列：
  第 8 行：price: price 必須是數字
```

## 專案結構

```text
src/
  app.ts               # 建立 Express app（可注入 Store 方便測試）
  server.ts            # 進入點，讀取 PORT
  errors.ts            # AppError 與統一錯誤處理 middleware
  schemas.ts           # zod schema
  store.ts             # 記憶體資料層與商業規則
  routes/              # categories / products / movements 路由
  scripts/csv-to-json.ts
tests/
  api.test.ts          # supertest 測 API 路由
  csv-to-json.test.ts  # CSV 解析與轉換
data/
  export.csv           # 範例輸入
  products.json        # 轉換結果
```

## 技術堆疊

Express 5.3 · TypeScript 6.0 · zod 4.6 · Vitest 5 · supertest 7 · tsx 4 · ESLint 10 + typescript-eslint 8.72 · Prettier 3.9

## 授權

僅供學習使用。
