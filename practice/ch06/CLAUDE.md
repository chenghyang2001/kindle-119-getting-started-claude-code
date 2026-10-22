# K119 第 06 章練習


## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

## Stack

- React 19 + TypeScript（`strict: true`）+ Vite 8
- 測試：Vitest + @testing-library/react（jsdom）
- 不使用任何 UI 套件或 CSS 框架；樣式用 CSS Modules（`*.module.css`）
- 指令：`npm run dev`／`npm run build`／`npm test`

## Component Conventions

- 只用函式元件，**具名匯出**（`export function UserCard`），不用 `export default`
- 檔名與元件名同為 PascalCase：`UserCard.tsx`
- Props 以 `interface <元件名>Props` 宣告並放在元件上方，不用 `React.FC`
- 一個檔案只放一個元件
- 元件不直接呼叫 `fetch`，資料一律經由 `src/hooks/` 的 hook 取得

## Folder Structure

```text
src/
  api/          # 唯一可以碰網路的地方（見 src/api/CLAUDE.md）
  components/   # 展示型元件，PascalCase.tsx，測試放同目錄 *.test.tsx
  hooks/        # 自訂 hook，useXxx.ts，測試放同目錄 *.test.ts
  types/        # 共用型別（interface），不放邏輯
  App.tsx
  main.tsx
```

## Patterns

- 自訂 hook 以 `use` 開頭，回傳**物件**（`{ data, isLoading, error }`），不回傳陣列
- 非同步 hook 必須用 `AbortController` 在 unmount 時取消請求
- 載入中／錯誤／空資料三種狀態都要在元件中處理並顯示給使用者
- 型別用 `interface` 描述物件、`type` 描述聯集；匯入型別用 `import type`

## Prohibitions

- 禁止 `any`（必要時用 `unknown` 再收斂）
- 禁止 `export default`（例外：`vite.config.ts` 等工具設定檔，工具本身要求預設匯出）
- 禁止在 `src/api/` 以外呼叫 `fetch`
- 禁止 `console.log` 留在提交的程式碼
- 禁止新增 npm 套件（需要時先在回覆中說明理由）
- 禁止 `// @ts-ignore`、`// eslint-disable`
- 禁止自行 `git commit` 或修改 `.gitignore`，除非使用者明確要求（2026-10-22 會話中發現 `claude -p` 自行 commit，補上此條）

## Tests

- 每個新元件與 hook 都要有同目錄的測試檔（`*.test.tsx`／`*.test.ts`）
- 元件用 `@testing-library/react` 的 `render` + `screen`；hook 用 `renderHook`
- 測試中 mock `src/api/` 的函式，不打真網路
- 完成前必須 `npm test` 與 `npm run build` 皆通過

## 規則維護

- **會話中發現違規就寫回 CLAUDE.md**：只要發現產出違反規範，或發現規範沒寫清楚而導致 Claude 做了不想要的事，
  修正程式之外，必須同時在本檔（或對應子目錄的 CLAUDE.md）補上或改寫那條規則，並在條文後註明日期與原因
- 只規範某個子目錄的規則，寫進該子目錄的 CLAUDE.md（例如 API 層規則放 `src/api/CLAUDE.md`），不要塞進根目錄
