# K119 第 7 章「.claude 資料夾」快速演練筆記

> 快速 demo 模式：未經 QA／審查。Claude Code 2.1.307，Windows 11 + Git Bash，2026-10-22。

## 做了什麼

| 元件 | 檔案 | 用途 |
| --- | --- | --- |
| Slash command | `.claude/commands/review-pr.md` | 審查目前變更，委派 `reviewer` agent，並套用 `security-checker` skill |
| Slash command（帶參數） | `.claude/commands/explain.md` | 用 `$ARGUMENTS` 接收要解釋的檔案 |
| Skill | `.claude/skills/security-checker/SKILL.md` | 安全檢查清單（寫死的機密、明文比對、注入、XSS、log 洩漏） |
| Subagent | `.claude/agents/reviewer.md` | 唯讀審查員，`tools: Read, Grep, Glob` |
| Rule | `.claude/rules/no-console-log.md` | 用 `paths: src/**/*.js` 限定範圍，禁止 `console.log` |
| Hook | `.claude/settings.local.json` | `PostToolUse`，matcher 是 `Write\|Edit`，在 `.claude/hook.log` 追加一行 |
| 測試標的 | `src/login.js` | 故意放了 2 個 `console.log` 和寫死的密碼 |

為了讓驗證可以追蹤，每個元件的輸出都規定要加標記：`[command:…]`、`[agent:reviewer]`、`[skill:security-checker]`、`[rule:no-console-log]`。

驗證指令一律用這個格式：
`env -u CLAUDECODE -u CLAUDE_CODE_… claude -p "<prompt>" --dangerously-skip-permissions --setting-sources project,local --output-format stream-json --verbose`
（執行前會把所有 `CLAUDE*` 環境變數清掉）

## 驗證證據

### 1. `/explain src/login.js`：command 加 `$ARGUMENTS` ✅
- 輸出第一行：`[command:explain] 目標：src/login.js`，表示 `$ARGUMENTS` 有正確代入。
- 逐行解釋，並把第 5、7 行標成 `[rule:no-console-log]`。

### 2. `/review-pr`：command、agent、skill ✅
- init 事件顯示有載入：agents 裡有 `reviewer`；skills 和 slash_commands 裡有 `security-checker`、`explain`、`review-pr`。
- 主流程的工具呼叫：`Bash(git status/diff)` → `Agent(subagent_type="reviewer")` → `Skill(skill="security-checker")`。
- **reviewer 子代理只用了 `Glob` ×2、`Read` ×1**，沒有 Bash 或 Write，可見 `tools` 白名單有生效。
- 輸出有 `[agent:reviewer]` 和 `[skill:security-checker]` 兩個區塊；security-checker 找到 3 個 🔴（L2 寫死密碼、L5 log 印出密碼、L6 用明文比對密碼）。結論是 REQUEST_CHANGES。
- 小瑕疵：reviewer 摘要寫「3 處 console.log」，實際只有 2 處。表格和規則區塊列的都是正確的 2 處，屬於模型的計數錯誤。

### 3. Rule 自動套用 ✅（另外補做的乾淨測試）
- `/explain` 的指令本身就要求模型去參考 `.claude/rules/`，而模型也真的用 Bash 讀了那個檔，所以那次的結果**不能證明**規則是自動注入的。
- 因此補跑一次：只准用 `Read` 讀 `src/login.js`。工具紀錄確認只呼叫了一次 Read，模型仍然逐字引用出「# 規則：禁止 console.log」和 `[rule:no-console-log]` 這個標示格式。結論是：讀到符合 `paths` 的檔案時，規則會自動載入。

### 4. PostToolUse hook ✅
- 先在 Git Bash 用假的 stdin JSON 手動測過指令。
- 再用 `claude -p` 叫模型 Write 新檔，接著 Edit 它。`.claude/hook.log` 多了兩行：
  ```
  2026-10-22 11:40:09 PostToolUse tool=Write file=…\src\hello.txt
  2026-10-22 11:40:11 PostToolUse tool=Edit file=…\src\hello.txt
  ```
  （測試檔 `src/hello.txt` 已刪除）

## 和書上做法的差異

> 這裡沒有逐字對照書本原文，以下是根據書中 `.claude` 資料夾章節的一般做法，整理出這次刻意改動的地方。

1. **Hook 寫在 `settings.local.json`**，沒有寫在共享的 `settings.json`。這是使用者的限制：不動全域設定，也不讓 hook 跟著 repo 被所有人套用。
2. **Hook 指令是 Windows Git Bash 版**：用 `jq` 解析 stdin 的 JSON，路徑用 `${CLAUDE_PROJECT_DIR:-.}`，沒有寫死絕對路徑。書上的範例多半預設 macOS 或 Linux。
3. **加了驗證用的標記字串**（`[agent:reviewer]` 等），這樣才能從 `claude -p` 的輸出客觀判斷元件有沒有作用。書上是用互動模式肉眼觀察。
4. **用 `--setting-sources project,local` 做隔離**，加上 `stream-json` 記錄工具呼叫，用來證明 subagent 的工具白名單。
5. **rule 加了 `paths` frontmatter**，只套用在 `src/**/*.js`，所以補做了「規則自動注入」的獨立驗證。
6. 觀察：新版 Claude Code 裡 skill 也會出現在 slash_commands 清單（可以用 `/security-checker` 直接叫出來），commands 和 skills 的界線比書上描述的模糊。

## 已知未處理風險
- `--setting-sources project,local` 只排除了全域的 **settings**。rule 測試的回答裡還是提到了「全域安全規則」，表示使用者層級的 CLAUDE.md 記憶可能仍然被載入了，沒有完全隔離。
- 驗證紀錄（`.claude/verify/*.jsonl`、`hook.log`）含本機路徑，已 gitignore，沒有 commit。
