# 專案地圖（MAP）

## 用途
小型帳務工具：依「當月實際使用天數」計算訂閱費的按比例金額（proration），
並把發票資料匯出成 CSV／Excel（以 TSV 模擬）等格式。

## 模組
| 路徑 | 職責 |
| --- | --- |
| `src/billing/proration.py` | `days_in_month()` 算當月天數；`prorate()` 依使用天數按比例計費；`upgrade_credit()` 月中升級方案的補差額 |
| `src/export/csv_generator.py` | `CsvGenerator`：驗證欄位 → 產出 CSV 字串 → 存檔 |
| `src/export/excel_generator.py` | `ExcelGenerator`：同上流程，但輸出 TSV（CRLF、UTF-8 BOM、欄名大寫、尾列 TOTAL） |
| `tests/` | pytest 測試（proration 6 個、export 4 個） |

## 技術
- Python ≥ 3.10，只用標準庫（`csv`、`io`、`math`、`datetime`）
- 套件管理：uv（虛擬環境在專案 `.venv`），測試：pytest（`pythonpath = ["src"]`）

## 最複雜／風險最高處
1. **`prorate()` 的金額捨入**：用 `math.floor(amt * 100) / 100` 無條件捨去，
   又是 float 運算 → 金額會少一分錢（測試 `45.83 != 45.84` 失敗）。牽涉金錢，影響最大。
2. **`upgrade_credit()`** 依賴 `prorate()` 兩次的結果相減，上游捨入錯誤會被放大。
3. 兩個 exporter 的欄位定義 `COLUMNS` 與 `validate()` 重複貼上，沒有共用基底，日後新增格式容易不一致。
