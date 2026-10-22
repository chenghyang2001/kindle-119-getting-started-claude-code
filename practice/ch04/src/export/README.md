# export 模組

把發票資料（`list[dict]`）匯出成不同檔案格式。每種格式一個類別，介面完全一致。

## 輸入資料格式

每一列是一個 dict，必須包含三個欄位：

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `invoice_id` | str | 發票編號 |
| `customer` | str | 客戶名稱（可含中文） |
| `amount` | int / float | 金額，輸出時固定兩位小數 |

缺欄位時 `render()` 會拋 `KeyError`。

## 可用的產生器

| 類別 | 檔案 | `ext` | 輸出特性 |
| --- | --- | --- | --- |
| `CsvGenerator` | `csv_generator.py` | `csv` | 逗號分隔、LF、UTF-8 |
| `ExcelGenerator` | `excel_generator.py` | `xls.tsv` | Tab 分隔、CRLF、UTF-8 BOM、欄名大寫、尾列 `TOTAL`（以 TSV 模擬 Excel，免裝 openpyxl） |
| `MarkdownGenerator` | `markdown_generator.py` | `md` | Markdown 表格，金額欄靠右，自動跳脫 `\|` 與換行 |

## 用法

```python
from export.markdown_generator import MarkdownGenerator

rows = [{"invoice_id": "INV-1", "customer": "Acme", "amount": 45.84}]
gen = MarkdownGenerator(rows)
print(gen.render())                     # 取得字串
gen.save(f"invoices.{gen.ext}")         # 寫檔，回傳路徑
```

## 共同模式（新增格式時照做）

1. 模組層級定義 `COLUMNS = ["invoice_id", "customer", "amount"]`
2. 類別屬性 `ext`（副檔名）
3. `__init__(self, rows)` 只存資料
4. `validate()` 檢查每列都有 `COLUMNS` 的欄位，缺了拋 `KeyError`
5. `render()` 先呼叫 `validate()`，再回傳完整字串（不碰檔案系統，方便測試）
6. `save(path)` 用 `render()` 的結果寫檔（明確指定 encoding、`newline=""`），回傳 `path`
7. 在 `tests/` 加對應測試：正常輸出、缺欄位、存檔

## 已知技術債

三個類別的 `COLUMNS`、`validate()`、`save()` 是重複的；格式再增加時，
建議抽出 `BaseGenerator` 基底類別，只讓子類別實作 `render()` 的格式部分。
