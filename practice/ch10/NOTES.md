# K119 第 10 章「除錯與復原」演練筆記

快速 demo 模式（主 Claude 直接寫檔，沒有派 QA／reviewer）。Python + uv + pytest。

## 做了什麼

| 步驟 | 內容 | commit |
| --- | --- | --- |
| 0 | 建 `src/api/search.py`，第 47 行 `scoped = [doc for doc in source if doc.tenant_id == tenant_id]`；6 個測試（含「不同 tenant 看不到彼此資料」） | `5ca2945` checkpoint |
| 1 | 清掉所有 `CLAUDE*` 環境變數，用 `claude -p --dangerously-skip-permissions` 請它加分頁（**沒有**加 tenant 約束，當對照組） | — |
| 2 | 用 `git diff` 檢查 tenant 過濾，確認沒被動到，測試通過後 commit | `5dd641b` |
| 3 | 照書上精確 6 步驟寫交易式 `process_pending_orders()`（`src/orders.py`），inventory／warehouse 用假物件 | `4ad484d` |
| 4 | 寫 `RECOVERY.md`，在暫存分支 `demo/recovery` 各示範一次 restore／reset --soft／reset --hard／revert，示範完已刪除分支 | 最後一個 commit |

## 步驟 2：tenant 過濾檢查過程

指令：

```bash
env $(env | grep -E '^CLAUDE' | cut -d= -f1 | sed 's/^/-u /') \
  claude -p --dangerously-skip-permissions "Add pagination to the search function ... Do not commit."
git diff --stat
git diff src/api/search.py
grep -n "tenant_id ==" src/api/search.py
uv run pytest -q
```

結果：

- `git diff --stat`：`search.py` +30／-3，`test_search.py` +61。
- 過濾那行**原封不動**，只因為上方新增了 `DEFAULT_PAGE_SIZE`、`MAX_PAGE_SIZE`、`_validate_pagination()`，從第 47 行移到第 71 行。
- diff 重點：
  - `search()` 新增 keyword-only 參數 `page=1`、`page_size=20`（上限 100），用 `TypeError`／`ValueError` 驗證（也排除 `bool`）。
  - 切片 `matched[start : start + page_size]` 放在**租戶過濾之後**，claude 還自己加了註解「分頁必須在租戶過濾之後切片」。
  - 新增 `test_pagination_applied_after_tenant_filter`：兩個租戶資料交錯，確認每頁只有自己租戶。
- 測試：6 → 22 個，全部通過。
- 判定：**過濾沒被拿掉**，所以不用 `git restore` 重做，也沒用「THAT FILTER MUST NOT BE TOUCHED」強化 prompt。

## 步驟 3：交易式訂單處理

- 6 步驟照書上原文（`kindle-119-getting-started-claude-code/teaching/ask/ch8-11.txt`）：查 pending → `check_availability` → `reserve` 並改 `processing` → `create_delivery_note` → `notify` → 沒庫存就維持 pending 並記 warning。
- 交易做法：用 `_UndoLog` 記下本次的狀態變更、庫存保留、出貨單；任何例外 → 反向撤銷全部再重新拋出（整批 all-or-nothing）。
- 測試 11 個：正常流程、庫存不足維持 pending＋warning、只動 pending 訂單、空表、步驟 1 失敗，以及步驟 2／3（reserve）／3（改狀態）／4／5 **在第二筆訂單失敗時，第一筆也一起回滾**，另測第一筆就失敗。
- 反向驗證：暫時把 `_rollback(...)` 換成 `pass`，有 6 個測試失敗，確認測試真的抓得到「沒回滾」的問題，之後已還原。

## 驗證結果

- `uv run pytest -q`：**33 passed**（search 22 + orders 11）。
- 最後 `git log` 只有 master 上的正式 commit，暫存分支 `demo/recovery` 已刪除。

## 和書上做法的差異

1. **對照組結果不同**：書上的情境是 AI 加分頁時把 tenant 過濾拿掉，所以要 restore 後用 `THAT FILTER MUST NOT BE TOUCHED` 重下 prompt。這次 claude 沒拿掉過濾，強化 prompt 那段沒有實際跑，只記錄檢查過程。
2. **交易範圍**：書上只說「任何一步失敗就回滾訂單與庫存」，沒講是單筆還是整批。這裡選整批 all-or-nothing，並在失敗後重新拋出例外讓呼叫端知道。
3. **出貨單補償**：書上沒要求。出貨單在外部倉庫系統，無法真的回滾；這裡多做了一步：如果 warehouse 有 `cancel_delivery_note()` 就呼叫它取消。已經送出的 `notify()` 收不回來，正式系統要另外做補償通知或 outbox 模式。
4. **資料庫是假的**：orders table 用記憶體 dict，「回滾」是自己記 undo log；正式環境應該用 DB 交易（`BEGIN`／`ROLLBACK`）處理訂單，庫存與倉庫用補償動作。
5. **書上沒提到的雜項**：子 claude 的 hook 會在專案寫 `.claude/session-state.md`，已加進 `.gitignore`。

## 已知沒處理的風險（快速模式）

- 沒有平行執行／重複執行同一批訂單的鎖（兩個 worker 同時跑會重複保留庫存）。
- 回滾途中如果 `release()` 失敗只記 log，庫存可能和實際不一致。
