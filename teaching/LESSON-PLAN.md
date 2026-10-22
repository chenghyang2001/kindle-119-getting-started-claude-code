# K119 快速演練課表

依據：NotebookLM 筆記本 `505bfc47…`（書 PDF）回答的「各章讀者實際動手操作」，原文在 `teaching/ask/`（2026-10-22 查詢）。
書上的練習多半是「拿你自己的既有專案」來做，這裡每章先在練習資料夾建一個最小的示範專案，再照書上的提示詞操作。

每段提示詞前面都要加：「全自動執行：不要問我任何問題、不要用選擇題，所有選擇一律採用你的推薦，直接做完並回報」。

## 共通限制（每章都適用）

- **絕不執行** `/logout`、`/login`、`/upgrade`、`/install-github-app`、`/statusline`、`/doctor`，不修改全域 `~/.claude/` 底下任何檔案；書上寫全域的一律改專案層。
- `claude mcp add`、`claude plugin install` 一律 `--scope project`。
- 不設 `ANTHROPIC_API_KEY`；需要第三方 token（SendGrid、Stripe、Slack、GitHub）的一律 mock 或只寫範本。
- 不建 GitHub repo、不 push、不部署；Python 套件裝在專案 `.venv`（用 uv），Node 套件裝在專案內。
- 練習中要用 `claude -p` 時先清 `CLAUDE*` 環境變數。
- 每章產出 `NOTES.md`：做了什麼、驗證結果、和書上做法的差異。完成後 git add＋commit。

## 各章提示詞

| 章 | 主題 | 要練習視窗做的事 |
| --- | --- | --- |
| 01 | Claude Code 的一天 | 先建一個最小 Express 專案（`src/users`、`src/orders` 兩個模組＋`src/shared/routes.js`），再照書上的流程：探索程式碼寫 `MAP.md`（架構、模式、副作用處理、通知系統該放哪）→ 只提架構不寫程式寫 `ARCH.md`（檔案結構＋每檔摘要）→ 實作一個最小 `src/notifications/`（只做 console 版，不接 SendGrid）→ 以 tech lead 身分審查並把結果寫進 `REVIEW.md` → commit。不開 PR |
| 02 | 上手第一小時 | 建 Python 專案：`utils/calculator.py` 的 `calculate_discounted_price(price, discount, customer_code=None)`；加 Python 用 `.gitignore`；從 docstring 產生 `docs/index.html`（純 HTML 無外部依賴）；用 pytest 寫正常、邊界、例外測試，並補一個 `customer_code=None` 的案例；做 Flask `/api/quote`，用 Flask-Limiter 限每個 IP 每分鐘 10 次，超過回 429 JSON；寫測試連打 11 次第 11 次要 429；全部 pytest 通過，最後用三點摘要改了什麼 |
| 03 | 提問的藝術 | 建 TypeScript＋Jest 專案，放一個巢狀過深、驗證與業務邏輯混在一起的 `processOrder`（含既有測試）。照書上三步：先寫 `PLAN.md`（重構方式、不准先改程式）→ 只重構驗證（每個檢查抽成具名函式＋early return）→ 再把兩個 db 寫入包進交易（用假 db 物件）；每步跑 `npm test` 維持通過。另寫 `PROMPTS.md`：把書上的「Context＋Goal＋Constraints」與「先要計畫再動手」各舉一個自己改寫的例子 |
| 04 | 既有程式碼 | 建一個沒有文件的「舊專案」：`src/billing/proration.py`（埋一個四捨五入錯誤，讓 `assert 45.83 == 45.84` 類測試失敗）、`src/export/csv_generator.py`、`excel_generator.py`（可用 csv 模擬）。照書上：探索後寫 `MAP.md`（用途、模組、技術、最複雜處）→ 讀失敗測試找出原因並修好 → 分析兩個 exporter 的共同模式後，照同模式加 `markdown_generator.py` → 為 `proration.py` 補 Google Style docstring → 產生 `src/export/README.md`；pytest 全過 |
| 05 | AI 測試安全網 | 建 `payments/`：`validators.py`（Luhn 卡號、到期日、CVV）、`gateway.py`、`processor.py`。照書上：先列功能與關鍵邊界寫進 `TEST-PLAN.md` → 用 `pytest.mark.parametrize` 寫 validators 測試 → 完整 mock gateway 測 processor（拒絕、逾時、重試、Payment 狀態）→ TDD：先只寫 rate limiter 測試（每 IP 每分 100 次、60 秒重置、白名單、超限回 429＋Retry-After），再實作讓它通過（用記憶體儲存取代 Redis）；pytest 全過 |
| 06 | CLAUDE.md 基本規則 | 建最小 React＋TypeScript（Vite）專案骨架，照書上範例寫專案根目錄 `CLAUDE.md`（Stack／Component Conventions／Folder Structure／Patterns／Prohibitions／Tests 六段）＋子目錄 `src/api/CLAUDE.md`（只規範 API 層）。然後用 `claude -p` 請它新增一個元件與一個 hook，檢查產出是否遵守規範並寫進 `NOTES.md`；再補一條「會話中發現違規就寫回 CLAUDE.md」的規則。全域 `~/.claude/CLAUDE.md` 只寫範本到 `templates/global-CLAUDE.md`，不可動真的 |
| 07 | .claude 資料夾（isolated） | 在專案建 `.claude/commands/review-pr.md`、帶 `$ARGUMENTS` 的 `.claude/commands/explain.md`、`.claude/skills/security-checker/SKILL.md`、`.claude/agents/reviewer.md`（只給 Read／Grep／Glob）、`.claude/rules/no-console-log.md`，並在 `.claude/settings.local.json` 加一個 PostToolUse hook（寫檔後記一行 log）。放一個含 console.log 與寫死密碼的小檔案，用 `claude -p "/explain src/xxx"` 與 `/review-pr` 實際觸發，驗證 agent、skill、hook 都有作用 |
| 08 | Git 實戰工作流 | 建小專案並在 main 有初始 commit。照書上：開 `feature/password-change-notifications` 分段實作並每段 commit（email 服務 mock SendGrid、HTML 範本、change_password 整合、測試）→ 用 Conventional Commits 產生訊息 → 刻意製造兩個分支在 `src/pricing.py` 的衝突並合併兩邊邏輯解決 → `git stash push -m` 再 `pop` → 練 `git reset HEAD~1`（保留修改）與 `git revert` → 產生 `PR.md`（做了什麼、怎麼手動測、設計決策）。不 push、不開 PR |
| 09 | 日常實用食譜 | 選三道食譜：① 依 schema（products／categories／movements）做 Express＋TypeScript REST API，zod 驗證、一致的錯誤處理（資料用記憶體，不接 PostgreSQL），用 supertest 測主要路由；② 寫 TypeScript 腳本把 `data/export.csv` 轉成 `data/products.json`；③ 設定 ESLint＋Prettier（＋`.editorconfig`）並跑一次 lint。最後依專案實際內容寫一份專業 `README.md` |
| 10 | 除錯與復原 | 先做 checkpoint commit。建 `src/api/search.py`（第 47 行附近依 tenant_id 過濾）。請它加分頁 → 用 `git diff` 檢查 tenant 過濾有沒有被動到（若被拿掉就 `git restore` 後用「THAT FILTER MUST NOT BE TOUCHED」加強約束重做，沒被拿掉也要在 NOTES 記錄檢查過程）→ 依書上精確 6 步驟寫交易式 `process_pending_orders()`（inventory／warehouse 用假物件，任何一步失敗要回滾）並寫測試 → 寫 `RECOVERY.md` 整理 git restore／reset --soft／reset --hard／revert 何時用 |
| 11 | 代理式程式設計入門 | 用 `claude -p`（先清 CLAUDE* 環境變數）寫 `scripts/review.sh` 對單一檔案做效能審查並存成報告；建 `.git/hooks/pre-push`：把 diff 交給 `claude -p` 審查資安，回 `BLOCK` 就擋下、`OK` 就放行，用一個含假密碼的 diff 實測會 BLOCK、修掉後會 OK（直接執行 hook 腳本模擬，不真的 push）；CI／cron 自動開 PR 的流程只寫 `.github/workflows/claude-review.yml` 範本與 `AUTOMATION.md` |
