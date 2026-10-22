---
description: 審查目前的變更（未提交與 src/ 內檔案），委派 reviewer agent 並套用 security-checker skill
allowed-tools: Read, Grep, Glob, Bash(git status:*), Bash(git diff:*), Task
---

# /review-pr

請審查本專案目前的變更：

1. 先用 `git status` 與 `git diff` 了解變更範圍；若沒有 diff，就審查 `src/` 下所有檔案。
2. **使用 `reviewer` subagent** 做程式碼審查（把要審的檔案清單交給它）。
3. **使用 `security-checker` skill** 檢查安全問題。
4. 套用專案規則（`.claude/rules/`）中的要求。

輸出格式（繁體中文）：

- 第一行固定輸出 `[command:review-pr]`
- `## Reviewer 結果`：貼上 reviewer agent 的回報（應以 `[agent:reviewer]` 開頭）
- `## 安全檢查`：security-checker skill 的結果（應以 `[skill:security-checker]` 開頭）
- `## 規則違反`：列出違反專案規則的地方，每條前面標 `[rule:...]`
- `## 結論`：APPROVE / REQUEST_CHANGES
