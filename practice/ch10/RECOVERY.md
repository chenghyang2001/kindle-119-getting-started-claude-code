# 復原指令速查（K119 第 10 章）

AI 改壞程式時，先問兩個問題：**改動 commit 了嗎？** **commit 推出去（分享給別人）了嗎？**

| 狀況 | 指令 | 效果 | 風險 |
| --- | --- | --- | --- |
| 改動還沒 commit，想整個丟掉 | `git restore <檔案>`（或 `git restore .`） | 工作目錄回到上一次 commit 的內容 | 未 commit 的改動直接消失，無法找回 |
| 只想把檔案移出 staging | `git restore --staged <檔案>` | 取消 `git add`，改動仍保留 | 無 |
| 剛 commit、還沒 push，想重寫訊息或重新整理 | `git reset --soft HEAD~1` | 撤銷 commit，改動留在 staging | 低：改動都還在 |
| 剛 commit、還沒 push，整個不要了 | `git reset --hard HEAD~1` | 撤銷 commit 並丟棄所有改動 | 高：未 commit 的東西一起消失（可用 `git reflog` 救回已 commit 的） |
| 已經 push / 別人可能拉過 | `git revert <commit>` | 新增一個「反向」commit，不改寫歷史 | 低：歷史保留，最安全 |

## 原則

1. **動 AI 之前先做 checkpoint commit**，之後所有復原都有基準點。
2. AI 改完先 `git diff` 看關鍵段落（例如 tenant 過濾）有沒有被動到，再跑測試。
3. 只要有疑慮就用 `restore`／`revert` 這類不丟資料的指令；`reset --hard` 前先 `git status` 確認沒有想留的東西。
4. 已分享的歷史只用 `revert`，不要 `reset` 後強推。

## 本專案的實際示範（暫存分支 `demo/recovery`，示範完已刪除）

1. **restore**：用 sed 把 `doc.tenant_id == tenant_id` 改成 `True`（模擬 AI 拿掉過濾）→ `git diff --stat` 顯示 1 行變動 → `git restore src/api/search.py` → 工作目錄乾淨。
2. **reset --soft**：新增 `demo.txt` 並 commit「示範 commit A」→ `git reset --soft HEAD~1` → commit 消失，`git status` 顯示 `A  demo.txt`（改動仍在 staging）。
3. **reset --hard**：再 commit「示範 commit B」→ `git reset --hard HEAD~1` → commit 與 `demo.txt` 都消失（`ls demo.txt` 找不到檔案）。
4. **revert**：commit「示範：錯誤地拿掉 tenant 過濾」→ `git revert --no-edit HEAD` → 歷史多一個 `Revert "..."` commit，`grep` 確認過濾那行回來了。
5. `git switch master && git branch -D demo/recovery`，master 歷史沒有受影響。
