# K119 第 8 章「Git 實戰工作流」練習筆記

快速 demo 模式（未經 QA／審查）。日期：2026-10-22。不 push、不開 PR、未改任何全域設定（只用 `git config --local core.autocrlf false` 消除 CRLF 警告）。

## 做了什麼

| 步驟 | 內容 | 結果 |
| --- | --- | --- |
| 0 | `uv init --bare` 建專案 + pytest，初始 commit，`master` 改名 `main` | `2553a01` |
| 1 | 開 `feature/password-change-notifications`，分 4 段 commit（Conventional Commits） | `3de2699` email 服務（mock SendGrid）→ `a8b2a0a` HTML 範本 → `ca201bb` change_password 整合 → `66c749f` 測試 |
| 2 | `feature/member-discount`（會員 9 折）與 `feature/bulk-discount`（滿 1000 折 50）改同一段 `src/pricing.py` | 第二次 merge 衝突（pricing.py + test_pricing.py），保留兩邊邏輯解決 → merge commit `e01c326` |
| 3 | `git stash push -m` → 切到 main 再切回 → `git stash pop` | 第一次失敗（見下方「踩坑」），重做成功 |
| 4a | 先 commit 一個訊息爛的 `wip`，`git reset HEAD~1` 保留修改，重新 commit | `d4edf8a wip` 消失，改成 `5921077 refactor(email): ...` |
| 4b | commit 一個 debug print，再 `git revert HEAD` 撤銷 | `7d6f05f` 被 `de5a099 Revert ...` 抵銷 |
| 5 | 產生 `PR.md`（做了什麼、手動測試、設計決策） | 見 PR.md |

## 驗證結果

- `main`：`uv run pytest -q` → **7 passed**（含新增的「會員 + 滿額同時成立 = 850」測試）。
- `feature/password-change-notifications`：`uv run pytest -q` → **9 passed**。
- 手動測試（PR.md 內的指令）輸出 `True` 與 `alice@example.com 您的密碼已變更`。
- `git stash list` 在 pop 後為空；revert 後 `grep DEBUG src/email_service.py` 為 0。

## 踩坑

- **stash 第一次失敗**：我用一個 `run` 函式（`eval "$@"`）同時執行指令並寫紀錄，`git stash push -m "WIP: add default sender..."` 的引號被吃掉，git 把後面的字當成檔案路徑而報錯，stash 沒建立。後續指令照跑，該修改就被直接 commit 成 `8e18865 feat(email): add default sender constant`。重做時把整段指令包在單引號內傳入就正常了。教訓：包裝 git 指令的 shell 函式要小心引號；每步要看輸出，不能只看最後結果。
- Windows 上初始 `git add` 出現 LF→CRLF 警告，之後設 local `core.autocrlf false` 消除。

## 和書上做法的差異

- **書上是對 Claude 下自然語言指令**（「幫我開分支」「分段 commit」「幫我解衝突」），由 Claude 在互動中逐步執行；這裡是全自動一次跑完，沒有人工確認每一步。
- **衝突是刻意製造的**：書上的情境是兩個人／兩個分支自然產生衝突；這裡用兩個短命分支故意改同一行。合併順序是 member 先 fast-forward 進 main，bulk 再 merge 產生衝突。
- **SendGrid 用 mock**：沒有真的 API key，也沒裝 `sendgrid` 套件；`MockSendGridClient` 只模擬回傳 202。
- **沒有 push、沒開 GitHub PR**：書上最後會用 `gh pr create`；這裡改產生 `PR.md` 當 PR 描述草稿。
- **feature 分支沒合回 main**：保留給「PR 審查後再合併」的情境；PR.md、NOTES.md 也 commit 在 feature 分支上。
- 專案用 `uv init --bare` + `src/` 平鋪模組（pytest 用 `pythonpath = ["src"]`），比書上可能用的套件結構更簡化。

## 每個 git 操作的指令與結果

以下為實際執行的指令與完整輸出（依時間順序）。

### 0. 初始 commit 與分支改名為 main

```
$ git add .gitignore README.md pyproject.toml uv.lock src tests CLAUDE.md
warning: in the working copy of '.gitignore', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'CLAUDE.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'README.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'pyproject.toml', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/pricing.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/users.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tests/test_pricing.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tests/test_users.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'uv.lock', LF will be replaced by CRLF the next time Git touches it

$ git commit -q -m "chore: initial project scaffold with uv and pytest" && git log --oneline
2553a01 chore: initial project scaffold with uv and pytest

$ git branch -m master main


$ git branch
* main

```

### 1. feature/password-change-notifications 分段實作

```
$ git switch -c feature/password-change-notifications
Switched to a new branch 'feature/password-change-notifications'

$ git add src/email_service.py


$ git commit -q -m "feat(email): add email service with mocked SendGrid client" && git log --oneline -1
3de2699 feat(email): add email service with mocked SendGrid client

$ git add src/templates/password_changed.html src/notifications.py


$ git commit -q -m "feat(email): add HTML template for password change notification" && git log --oneline -1
a8b2a0a feat(email): add HTML template for password change notification

$ git add src/users.py


$ git commit -q -m "feat(auth): send notification email after password change" && git log --oneline -1
ca201bb feat(auth): send notification email after password change

$ uv run pytest -q 2>&1 | tail -1
9 passed in 0.04s

$ git add tests/test_password_notifications.py


$ git commit -q -m "test(auth): cover password change notification flow" && git log --oneline
66c749f test(auth): cover password change notification flow
ca201bb feat(auth): send notification email after password change
a8b2a0a feat(email): add HTML template for password change notification
3de2699 feat(email): add email service with mocked SendGrid client
2553a01 chore: initial project scaffold with uv and pytest

```

### 2. 刻意製造 src/pricing.py 合併衝突並解決

```
$ git switch main
Switched to branch 'main'

$ git switch -c feature/member-discount
Switched to a new branch 'feature/member-discount'

$ uv run pytest -q 2>&1 | tail -1
5 passed in 0.05s

$ git add src/pricing.py tests/test_pricing.py


$ git commit -q -m "feat(pricing): add 10% member discount" && git log --oneline -1
b20eaa6 feat(pricing): add 10% member discount

$ git switch main
Switched to branch 'main'

$ git switch -c feature/bulk-discount
Switched to a new branch 'feature/bulk-discount'

$ uv run pytest -q 2>&1 | tail -1
5 passed in 0.03s

$ git add src/pricing.py tests/test_pricing.py


$ git commit -q -m "feat(pricing): add bulk order discount" && git log --oneline -1
5b92d51 feat(pricing): add bulk order discount

$ git switch main
Switched to branch 'main'

$ git merge --no-edit feature/member-discount
Updating 2553a01..b20eaa6
Fast-forward
 src/pricing.py        | 2 ++
 tests/test_pricing.py | 4 ++++
 2 files changed, 6 insertions(+)

$ git merge --no-edit feature/bulk-discount
Auto-merging src/pricing.py
CONFLICT (content): Merge conflict in src/pricing.py
Auto-merging tests/test_pricing.py
CONFLICT (content): Merge conflict in tests/test_pricing.py
Automatic merge failed; fix conflicts and then commit the result.

$ git status --short
UU src/pricing.py
UU tests/test_pricing.py

$ cat src/pricing.py
"""訂單價格計算。"""


def calculate_total(subtotal: float, customer_type: str = "regular") -> float:
    if subtotal < 0:
        raise ValueError("小計不可為負數")
    total = subtotal
<<<<<<< HEAD
    if customer_type == "member":
        total = total * 0.9  # 會員 9 折
=======
    if subtotal >= 1000:
        total = total - 50  # 滿 1000 折 50
>>>>>>> feature/bulk-discount
    return round(total, 2)

```

衝突解決方式：兩個折扣都保留，先套會員 9 折、再判斷「原始小計」是否滿 1000 折 50；測試檔兩邊的測試都留下，並新增兩種折扣同時成立的測試。

```
$ uv run pytest -q 2>&1 | tail -1
7 passed in 0.03s

$ git add src/pricing.py tests/test_pricing.py


$ git commit -q --no-edit && git log --oneline --graph -5
*   e01c326 Merge branch 'feature/bulk-discount'
|\  
| * 5b92d51 feat(pricing): add bulk order discount
* | b20eaa6 feat(pricing): add 10% member discount
|/  
* 2553a01 chore: initial project scaffold with uv and pytest

$ git branch -d feature/member-discount feature/bulk-discount
Deleted branch feature/member-discount (was b20eaa6).
Deleted branch feature/bulk-discount (was 5b92d51).

```

### 3. git stash push -m / git stash pop

```
$ git switch feature/password-change-notifications
Switched to branch 'feature/password-change-notifications'

$ git status --short
 M src/email_service.py

$ git stash push -m WIP: add default sender to EmailService
error: pathspec ':(prefix:0)add' did not match any file(s) known to git
error: pathspec ':(prefix:0)default' did not match any file(s) known to git
error: pathspec ':(prefix:0)sender' did not match any file(s) known to git
error: pathspec ':(prefix:0)to' did not match any file(s) known to git
error: pathspec ':(prefix:0)EmailService' did not match any file(s) known to git
Did you forget to 'git add'?

$ git stash list


$ git status --short; echo "(工作區已乾淨)"
 M src/email_service.py
(工作區已乾淨)

$ git switch main && git log --oneline -1 && git switch feature/password-change-notifications
error: Your local changes to the following files would be overwritten by checkout:
	src/email_service.py
Please commit your changes or stash them before you switch branches.
Aborting

$ git stash pop
No stash entries found.

$ git status --short
 M src/email_service.py

$ uv run pytest -q 2>&1 | tail -1
9 passed in 0.15s

$ git add src/email_service.py


$ git commit -q -m "feat(email): add default sender constant" && git log --oneline -1
8e18865 feat(email): add default sender constant

```

### 4a. git reset HEAD~1（保留修改，重新 commit）

```
$ git add src/notifications.py


$ git commit -q -m "wip" && git log --oneline -2
d4edf8a wip
8e18865 feat(email): add default sender constant

$ git reset HEAD~1
Unstaged changes after reset:
M	src/notifications.py

$ git status --short
 M src/notifications.py

$ git diff --stat
 src/notifications.py | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

$ git add src/notifications.py


$ git commit -q -m "refactor(email): extract password changed subject constant" && git log --oneline -2
5921077 refactor(email): extract password changed subject constant
8e18865 feat(email): add default sender constant

```

### 4b. git revert（撤銷一個 commit）

```
$ git add src/email_service.py


$ git commit -q -m "chore(email): add debug print to mock client" && git log --oneline -1
7d6f05f chore(email): add debug print to mock client

$ git revert --no-edit HEAD && git log --oneline -3
[feature/password-change-notifications de5a099] Revert "chore(email): add debug print to mock client"
 Date: Thu Oct 22 11:44:21 2026 +0800
 1 file changed, 1 deletion(-)
de5a099 Revert "chore(email): add debug print to mock client"
7d6f05f chore(email): add debug print to mock client
5921077 refactor(email): extract password changed subject constant

$ grep -c "DEBUG" src/email_service.py || echo "DEBUG 已移除"
0
DEBUG 已移除

$ uv run pytest -q 2>&1 | tail -1
9 passed in 0.08s

```

### 3（重做）. git stash push -m / git stash pop — 正確引號版

```
$ git status --short
 M src/email_service.py

$ git stash push -m 'WIP: clarify EmailSendError docstring'
Saved working directory and index state On feature/password-change-notifications: WIP: clarify EmailSendError docstring

$ git stash list
stash@{0}: On feature/password-change-notifications: WIP: clarify EmailSendError docstring

$ git status --short && echo "(工作區已乾淨)"
(工作區已乾淨)

$ git switch main && git log --oneline -1 && git switch feature/password-change-notifications
Switched to branch 'main'
e01c326 Merge branch 'feature/bulk-discount'
Switched to branch 'feature/password-change-notifications'

$ git stash pop
On branch feature/password-change-notifications
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   src/email_service.py

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (8562ffe721870375cba49221afcf00c7e8a5c821)

$ git status --short && git stash list && echo "(stash 已清空)"
 M src/email_service.py
(stash 已清空)

$ uv run pytest -q 2>&1 | tail -1
9 passed in 0.06s

$ git add src/email_service.py


$ git commit -q -m "docs(email): clarify EmailSendError docstring" && git log --oneline -1
57767a9 docs(email): clarify EmailSendError docstring

```
### 最終分支圖

```
$ git log --oneline --graph --all
* 57767a9 docs(email): clarify EmailSendError docstring
* de5a099 Revert "chore(email): add debug print to mock client"
* 7d6f05f chore(email): add debug print to mock client
* 5921077 refactor(email): extract password changed subject constant
* 8e18865 feat(email): add default sender constant
* 66c749f test(auth): cover password change notification flow
* ca201bb feat(auth): send notification email after password change
* a8b2a0a feat(email): add HTML template for password change notification
* 3de2699 feat(email): add email service with mocked SendGrid client
| *   e01c326 Merge branch 'feature/bulk-discount'
| |\  
| | * 5b92d51 feat(pricing): add bulk order discount
| |/  
|/|   
| * b20eaa6 feat(pricing): add 10% member discount
|/  
* 2553a01 chore: initial project scaffold with uv and pytest
```
