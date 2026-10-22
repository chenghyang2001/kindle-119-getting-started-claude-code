# src/api/ 規則（只適用 API 層）

- 所有 HTTP 呼叫都經過 `client.ts` 的 `apiGet`（或之後新增的 `apiPost` 等），不得在其他檔案直接用 `fetch`
- 每個資源一個檔案（`users.ts`、`posts.ts`），匯出以動詞開頭的函式：`fetchUsers`、`createPost`
- 函式回傳型別必須明確標註 `Promise<T>`，`T` 來自 `src/types/`
- 每個函式都接受可選的 `signal?: AbortSignal`，讓 hook 能取消請求
- 錯誤一律以 `ApiError`（含 `status`）丟出，不在 API 層吞錯或回傳 `null`
- API 層不得 import React，也不得 import `src/components/` 或 `src/hooks/`
- `BASE_URL` 只在 `client.ts` 定義一次；不得寫入金鑰或 token
