# K119 第 4 章「既有程式碼」演練筆記

> 快速 demo 模式：主 Claude 直接寫檔，未經 code-qa／code-reviewer 審查。

## 做了什麼

| 步驟 | 內容 | 產出 |
| --- | --- | --- |
| 0 | 建「沒有文件的舊專案」：uv + 專案 `.venv` + pytest；在 `prorate()` 埋 `math.floor` 無條件捨去的 bug | commit `097690d` |
| 1 | 探索程式碼後寫專案地圖：用途、模組、技術、最複雜處 | `MAP.md` |
| 2 | 讀失敗測試 `assert 45.83 == 45.84` → 49.00 × 29/31 = 45.8387，被 `math.floor(amt*100)/100` 捨成 45.83。改成 `Decimal(str(price))` 計算 + `ROUND_HALF_UP`；`upgrade_credit()` 的相減也改用 Decimal | `src/billing/proration.py` |
| 3 | 比對兩個 exporter 的共同模式（`COLUMNS`／`ext`／`validate→render→save`），照抄出 `MarkdownGenerator`，含 `\|` 與換行跳脫 | `src/export/markdown_generator.py`、`tests/test_markdown_generator.py` |
| 4 | `proration.py` 補 Google Style docstring（Args／Returns／Raises／Example），模組 docstring 說明捨入原則 | 同上 |
| 5 | 產生 export 模組說明：輸入格式、三種產生器比較、用法、新增格式的 7 步驟、技術債 | `src/export/README.md` |

## 驗證結果

- 修 bug 前：`uv run pytest` → 1 failed（`test_partial_month_rounding`，`45.83 == 45.84`）, 9 passed
- 修 bug 後 + 新增 markdown 測試：`uv run pytest` → **15 passed**
- docstring 內的 Example 用 `uv run python -m doctest src/billing/proration.py` 驗證 → 3 passed

## 和書上做法的差異

1. **書上是對著真實的舊專案提問**（「這個專案在做什麼？」「為什麼這個測試失敗？」）讓 Claude 探索；
   這裡舊專案是自己先造出來的，bug 位置事先已知，所以「探索」與「找原因」是演出來的，少了真正摸索陌生程式碼的過程。
2. **書上是一步一步互動對話**，每步看完 Claude 的回答再下下一個提示；這裡使用者要求全自動，一次跑完，沒有中途人工審視。
3. **Excel exporter 用 TSV 模擬**（依題目允許），書上若用 openpyxl，輸出會是真正的 `.xlsx`。
4. 書上修 bug 通常只示範改捨入方式；這裡順手把 `upgrade_credit()` 的相減也改成 Decimal，並在 README 註記重複程式碼的技術債（未實際重構，避免超出範圍）。
5. 依專案 CLAUDE.md 用快速模式，未走全域的 writer → QA → reviewer 三 agent 流程。

## 已知沒處理的風險

- 三個 exporter 仍有重複程式碼（未抽 `BaseGenerator`）。
- `prorate()` 回傳 float；金額若要繼續累加，呼叫端最好也用 Decimal。
- 不支援跨月計費（跨月直接拋 `ValueError`），與原行為相同。
