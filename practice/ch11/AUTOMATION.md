# 自動化流程說明（範本，尚未啟用）

本練習**沒有建 GitHub repo、沒有設定任何 secret**，以下只是啟用步驟的說明。

## 三層自動化

| 層級 | 觸發時機 | 檔案 | 擋不擋 |
| --- | --- | --- | --- |
| 本機 hook | `git push` 前 | `.git/hooks/pre-push`（版控副本 `scripts/pre-push`） | BLOCK 就擋 |
| CI（PR） | PR 開啟或更新 | `.github/workflows/claude-review.yml` 的 `security-review` | BLOCK 讓 check 失敗，並把結果留言到 PR |
| 排程（cron） | 每週一 09:00（台灣） | 同一個 workflow 的 `weekly-perf-pr` | 不擋；跑 `scripts/review.sh` 產報告，自動開 PR |

CI 與本機共用同一支 `scripts/pre-push`（透過 `--diff-file` 參數），規則只維護一份。

## 啟用步驟

1. 建 repo 並推上去（本練習未做）。
2. 在 repo **Settings → Secrets and variables → Actions** 新增 `ANTHROPIC_API_KEY`。
   - 只放 GitHub Secrets，**不要**設成本機全域環境變數，否則本機 `claude -p` 會改扣 API 額度而不是訂閱額度。
3. **Settings → Actions → General** 勾選「Allow GitHub Actions to create and approve pull requests」，排程任務才能開 PR。
4. 用 `workflow_dispatch` 手動觸發一次 `weekly-perf-pr` 確認流程。

## 本機另一種排程：cron／Windows 工作排程器

不想用 GitHub Actions 時，可以在本機排程：

```bash
# Linux／macOS crontab：每週一 09:00 對所有 .py 產報告
0 9 * * 1 cd ~/workspace/k119-ch11-practice && for f in src/*.py; do scripts/review.sh "$f"; done
```

Windows 用工作排程器（Git Bash 下要加 `MSYS_NO_PATHCONV=1`），本練習未建立排程。

## 注意事項

- 腳本開頭會清掉所有 `CLAUDE` 開頭的環境變數，避免在 Claude Code 裡呼叫時被當成巢狀 session。
- `claude -p` 呼叫失敗或回覆無法判讀時，hook 一律**擋下**（寧可誤擋，也不放行沒審過的程式碼）。
- 自動開的 PR 只是建議，一定要有人看過再合併。
