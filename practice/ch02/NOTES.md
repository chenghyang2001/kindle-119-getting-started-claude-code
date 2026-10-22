# K119 第 2 章「上手第一小時」演練筆記

> 快速 demo 模式：未經 QA／code review，只求看懂流程。

## 做了什麼

| 項目 | 檔案 |
| --- | --- |
| uv 專案、套件裝在專案 `.venv` | `pyproject.toml`、`uv.lock` |
| 折扣計算函式 | `utils/calculator.py` |
| Python 用 .gitignore | `.gitignore` |
| 從 docstring 產生文件 | `scripts/gen_docs.py` → `docs/index.html` |
| pytest 測試 | `tests/test_calculator.py`、`tests/test_api.py` |
| Flask `/api/quote` + Flask-Limiter | `app.py` |

`calculate_discounted_price(price, discount, customer_code=None)` 規格：

- `discount` 是 0～1 的比率（0.2 = 打八折）
- `customer_code`：`VIP` 再減 5%、`STAFF` 再減 10%（不分大小寫）；`None` 不加折扣；其他值丟 `ValueError`
- 負價、折扣超範圍 → `ValueError`；非數字（含 bool）→ `TypeError`
- 結果四捨五入到小數 2 位

`/api/quote` 支援 GET query 或 POST JSON（`price`、`discount`、`customer_code`），
每個 IP 每分鐘 10 次，超過回 `429` + `{"error": "too_many_requests", ...}`。

## 怎麼跑

```bash
uv sync                                  # 建 .venv 並安裝
uv run pytest -q                         # 跑測試
PYTHONUTF8=1 uv run python scripts/gen_docs.py   # 重產 docs/index.html
uv run python app.py                     # 啟動 http://127.0.0.1:5000/api/quote?price=100&discount=0.2
```

## 驗證結果

- `uv run pytest -q` → **21 passed**
  - 計算：正常 5（含 `customer_code=None` 專屬案例）、邊界 4、例外 8
  - API：正常報價、缺欄位 400、連打 11 次第 11 次 429（JSON）、不同 IP 各自計數
- `docs/index.html` 產生成功，無任何 `src=`／`href=` 外部依賴

## 和書上做法的差異

- **套件管理**：用 `uv`（`uv init --bare` + `uv add`），不是 `python -m venv` + `pip install`；依賴鎖在 `uv.lock`。
- **互動方式**：書上是在 Claude Code 裡一步步下 prompt、逐一確認；這次是一個 prompt 全自動跑完，選擇題都採預設推薦。
- **文件產生**：沒用 pdoc／Sphinx 等工具，自寫約 50 行腳本用 `inspect` 讀 docstring，確保純 HTML 零依賴。
- **速率限制儲存**：`memory://`，只適合單一程序；正式部署要換 Redis。
- **App factory**：用 `create_app()`，讓每個測試拿到獨立的限流計數器，測試不會互相干擾。
- 沒建 GitHub repo、沒 push（依指示）。

## 已知未處理的風險

- 在反向代理後面時 `get_remote_address` 會拿到代理 IP，需加 `ProxyFix`。
- 浮點數計算未用 `Decimal`，金額精度只靠 `round`。
