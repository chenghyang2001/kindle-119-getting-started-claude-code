# K119 第 11 章「代理式程式設計入門」演練筆記

> 快速 demo 模式：只跑冒煙測試與 BLOCK／OK 實測，未經 QA／審查 agent。

## 做了什麼

| 項目 | 檔案 | 說明 |
| --- | --- | --- |
| 練習專案 | `src/orders.py`、`src/config.py` | orders 刻意放三個效能問題；config 從環境變數讀密碼 |
| (1) 效能審查腳本 | `scripts/review.sh` | 清掉 CLAUDE* 環境變數 → 把檔案內容組進 prompt → `claude -p` → 存到 `reports/perf-<檔名>-<時間>.md` |
| (2) pre-push hook | `.git/hooks/pre-push`（版控副本 `scripts/pre-push`） | 讀 stdin 的 pre-push 格式算出 diff，或用 `--diff-file` 指定；第一行 `BLOCK` → exit 1，`OK` → exit 0 |
| (3) CI／cron 範本 | `.github/workflows/claude-review.yml`、`AUTOMATION.md` | PR 時跑資安審查並留言；每週排程跑效能審查並自動開 PR。只是範本，未建 repo、未設 secret |

## 驗證結果

### review.sh 實跑

`scripts/review.sh src/orders.py` → 34 秒完成，產出 `reports/perf-src_orders.py-20261022-120356.md`。
抓到 4 項：`find_duplicate_ids` O(n²)（高）、`total_by_customer` O(C·N)（高）、`build_report` 字串 `+=`（中）、整份報表放記憶體（低）。
錯誤路徑：不給參數、檔案不存在都會印錯誤並 exit 1。

### pre-push：含假密碼 → BLOCK

在暫時分支 `test/fake-secret` commit 了 `DB_PASSWORD = "SuperSecret123!"`，用 stdin 餵 pre-push 格式：

```text
$ printf 'refs/heads/test/fake-secret <local_sha> refs/heads/test/fake-secret <base_sha>\n' | .git/hooks/pre-push origin https://example.invalid/repo.git
[pre-push] Claude 資安審查中...
----- Claude 審查結果 -----
BLOCK
新增的行在 `src/config.py` 把資料庫密碼 `DB_PASSWORD = "SuperSecret123!"` 直接寫死在原始碼裡，換掉了原本從環境變數 `APP_DB_PASSWORD` 讀取的寫法。就算註解寫著「假密碼，練習用」，寫死的機密一樣要擋下來。
---------------------------
[pre-push] BLOCK：推送已擋下
EXIT_CODE=1
```

### pre-push：修掉密碼 → OK

再 commit 一次改回環境變數，同樣用 stdin 餵（base 不變）：

```text
[pre-push] Claude 資安審查中...
----- Claude 審查結果 -----
OK
新增的行只修改了錯誤訊息文字，提示使用者參考 `.env.example`；密碼仍然從環境變數讀取，沒有寫死的機密，也沒有注入或其他資安問題。
---------------------------
[pre-push] OK：放行
EXIT_CODE=0
```

另測空輸入：印「沒有要審查的變更，放行」，exit 0。
測完刪掉 `test/fake-secret` 分支，假密碼沒有進 master 歷史；全程沒有執行 `git push`。

## 和書上做法的差異

課表上的基本做法是「`claude -p` 審查 → 回 BLOCK／OK 決定擋不擋」。這次額外做了：

1. **環境變數清得更徹底**：用迴圈 unset 所有 `CLAUDE` 開頭的變數（本機 session 內實際有 13 個），不是只清一兩個固定名稱。
2. **不讓 `claude -p` 用工具**：檔案內容和 diff 直接放進 prompt，審查時不需要讀檔或執行指令，比較快也比較安全。
3. **判讀失敗一律擋下**：`claude -p` 失敗、找不到 CLI、第一行不是 BLOCK／OK，都 exit 1。
4. **hook 支援 `--diff-file`**：方便測試，也讓 CI 能重用同一支腳本，規則只維護一份。
5. **處理 pre-push 的邊界情況**：刪除遠端分支（local sha 全 0）跳過；新分支（remote sha 全 0）跟空 tree 比。
6. **加 `.gitattributes`** 讓 `.sh`、`pre-push`、`.yml` 固定 LF，避免 Windows 換行讓 hook 在 Linux CI 上壞掉。

## 已知限制

- **只看推送範圍的「淨 diff」**：如果先 commit 密碼、下一個 commit 又刪掉，淨 diff 看不到密碼，但密碼還在歷史裡、會被推上去。要擋這種情況，得逐個 commit 審查（`git log -p`），或另外用 gitleaks 這類工具。
- 結果靠 LLM 判斷，不保證每次一致；每次 push 多等約 20–30 秒。
- 大 diff 會整份塞進 prompt，沒有做長度上限。
- CI 範本沒實際跑過（沒有 repo 也沒有 secret）。
