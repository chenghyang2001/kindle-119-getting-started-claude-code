# K119 第 06 章練習筆記：CLAUDE.md 基本規則

> 快速 demo 模式，未經 QA／code review。

## 做了什麼

1. **建最小 React＋TypeScript（Vite）骨架**：手動寫 `package.json`、`tsconfig.json`、`vite.config.ts`、`index.html`、`src/main.tsx`、`src/App.tsx`，
   套件全部用 `npm install` 裝在專案內（React 19、Vite 8、TypeScript 7、Vitest 5、@testing-library/react、jsdom）。
   另外先放好 API 層範例：`src/api/client.ts`（`apiGet` + `ApiError`）、`src/api/users.ts`（`fetchUsers`）、`src/types/user.ts`。
2. **根目錄 `CLAUDE.md`**：保留最上方「本專案例外」，加上 Stack／Component Conventions／Folder Structure／Patterns／Prohibitions／Tests 六段。
3. **子目錄 `src/api/CLAUDE.md`**：只規範 API 層（一律走 `client.ts`、每資源一檔、明確回傳型別、接受 `AbortSignal`、以 `ApiError` 丟錯、不得 import React）。
4. **全域範本** `templates/global-CLAUDE.md`：示範個人層級該放的內容；**真正的 `~/.claude/CLAUDE.md` 沒動**。
5. **用 `claude -p` 測規範**：先用 `env -u CLAUDECODE -u CLAUDE_CODE_...`（清掉全部 13 個 `CLAUDE` 開頭的環境變數）＋`--dangerously-skip-permissions` 執行：

   > 請新增一個 UserList 元件和一個 useUsers hook：hook 透過 API 層取得使用者清單，元件顯示使用者名稱與 email。請遵守專案的 CLAUDE.md 規範，完成後跑測試與建置並簡短回報。

   它產出：`src/hooks/useUsers.ts`＋`.test.ts`、`src/components/UserList.tsx`＋`.test.tsx`＋`.module.css`，並把 `<UserList />` 放進 `App.tsx`。
6. **補規則**：在 `CLAUDE.md` 新增「規則維護」段（會話中發現違規就寫回 CLAUDE.md），並實際依此寫回兩條（見下方）。

## 驗證結果（逐條對照規範）

| 規範 | 結果 | 依據 |
| --- | --- | --- |
| 函式元件、具名匯出、無 `export default` | ✅ | `grep "export default" src` 無結果 |
| 檔名 PascalCase／hook 以 `use` 開頭 | ✅ | `UserList.tsx`、`useUsers.ts` |
| 元件不直接 `fetch`，經 hook → API 層 | ✅ | `src/api/` 以外沒有 `fetch(` |
| hook 回傳物件 `{ data, isLoading, error }` | ✅ | `useUsers.ts` |
| `AbortController` 在 unmount 取消 | ✅ | 並有測試驗證 `signal.aborted` |
| 載入中／錯誤／空資料三種狀態 | ✅ | `role="status"`、`role="alert"`、「目前沒有使用者。」 |
| `import type`、禁止 `any`／`console.log`／`@ts-ignore` | ✅ | grep 皆無結果；錯誤用 `unknown` 收斂 |
| 樣式用 CSS Modules | ✅ | `UserList.module.css` |
| 不新增 npm 套件 | ✅ | `package.json` 依賴未變 |
| 同目錄測試、mock API 層、用 `renderHook` | ✅ | `vi.mock('../api/users')` |
| `npm test`／`npm run build` | ✅ | 2 個測試檔、7 個測試全過；建置成功（JS 220.97 kB） |

### 發現的問題 → 寫回 CLAUDE.md

1. **`claude -p` 自行 commit 並改了 `.gitignore`**：它被本機 Stop hook 要求「不要留未提交變更」，於是自己做了兩個 commit
   （`新增 UserList 元件與 useUsers hook`、`更新 .gitignore 排除 session 狀態檔`），連我先 stage 好的骨架檔也一起包進去。
   原規範沒寫這點 → Prohibitions 補上「禁止自行 `git commit` 或修改 `.gitignore`，除非使用者明確要求」。
2. **`export default` 規則和工具衝突**：`vite.config.ts` 必須預設匯出，原條文沒有例外 → 改為「例外：工具設定檔」。

## 和書上做法的差異

- **版本較新**：書上範例年代的 React 18／TypeScript 5，這裡實際裝到 React 19、Vite 8、TypeScript 7；規範內容照新版寫。
- **骨架手動建立**：沒用 `npm create vite`（在非空目錄會跳互動問題），改手寫設定檔，結果等同 `react-ts` 範本的精簡版。
- **六段內容是自行改寫**：教材 repo 沒有書上原文，各段依書中結構（Stack／Component Conventions／Folder Structure／Patterns／Prohibitions／Tests）自行填入適合本專案的規則，並全部改成繁體中文。
- **用 `claude -p` 取代互動會話**：書上是在互動會話中請 Claude 寫元件；這裡用非互動模式，方便一次看完產出並逐條比對。
  也因此遇到本機 Stop hook 讓子程序自動 commit 的狀況，這是書上沒有的。
- **全域 CLAUDE.md 只寫範本**：書上會直接編輯 `~/.claude/CLAUDE.md`；本練習規定不動全域，所以放在 `templates/global-CLAUDE.md`。
- **多了「規則維護」段**：把「會話中發現違規就寫回」寫成明確規則，並在本次練習實際執行兩次。

## 已知未處理

- `useUsers` 在請求成功但元件剛好 unmount 的極短時間內仍會呼叫 `setData`（React 19 不會報錯，影響可忽略）。
- 沒有 ESLint，「禁止 `eslint-disable`」目前只是預防性條文。
