# K119 第 5 章練習筆記：AI 測試安全網

> 快速 demo 模式：主 Claude 直接寫檔，未經 code-qa／code-reviewer 審查。

## 做了什麼

1. 用 `uv init --lib` 建 `payments` 套件（src 版面，套件裝在專案 `.venv`，pytest 為 dev 依賴）。
   - `validators.py`：Luhn 卡號（13～19 位、允許空白／連字號）、到期日（含當月、兩位數年份）、CVV（Amex 4 位，其他 3 位）。
   - `gateway.py`：閘道介面＋`GatewayTimeout`／`GatewayError`，`charge()` 不真的連線。
   - `processor.py`：驗證 → 呼叫閘道 → 更新 `Payment` 狀態（PENDING／APPROVED／DECLINED／FAILED），只有逾時才重試。
   - 先 commit（`a6425bf`）。
2. 先寫 `TEST-PLAN.md`，列出每個功能的正常、邊界與錯誤情境，再照計畫寫測試。
3. `tests/test_validators.py`：全部用 `pytest.mark.parametrize`。
4. `tests/test_processor.py`：用 `create_autospec(PaymentGateway)` 完整 mock 閘道，涵蓋核准、拒絕（不重試）、逾時後成功、逾時用盡、閘道錯誤（不重試）、輸入不合法時「完全不呼叫閘道」、重複處理非 pending 付款。
5. TDD 做 rate limiter（`rate_limiter.py`）：每 IP 每分鐘 100 次、60 秒重置、白名單、超限回 429＋`Retry-After`。

## 驗證結果

| 階段 | 指令 | 結果 |
| --- | --- | --- |
| validators＋processor 測試 | `uv run pytest -q` | 43 passed |
| TDD 紅燈（commit `a264e30`） | `uv run pytest -q` | `ModuleNotFoundError: No module named 'payments.rate_limiter'`，collection 失敗 |
| TDD 綠燈 | `uv run pytest -v` | **56 passed**（新增 13 個 rate limiter 測試全過） |

紅燈的 commit 只含測試檔，可用 `git show a264e30 --stat` 確認當時沒有實作。

## 和書上做法的差異

| 書上 | 這次 | 原因 |
| --- | --- | --- |
| rate limiter 存 Redis | `InMemoryStore`（dict，介面對齊 get/set） | 不需要架 Redis；換 Redis 只要替換 store |
| 時間用系統時間，測試可能要等或 patch `time` | 建構時注入 `clock`，測試用 `FakeClock.advance()` | 測 60 秒重置不用真的等，也不用 monkeypatch |
| 一般用 `unittest.mock.Mock` | `create_autospec`，mock 會檢查方法簽名 | 呼叫參數寫錯時測試會直接失敗，不會默默通過 |
| 紅燈通常是 assertion 失敗 | 紅燈是「模組不存在」的 collection 錯誤 | 嚴格照「只寫測試」；缺點是看不到每個測試個別失敗 |
| 專案結構 `payments/` | uv 預設的 `src/payments/` | `uv init --lib` 的慣例，避免測試誤用未安裝的原始碼 |

## 已知限制（快速模式沒處理）

- 固定視窗演算法：視窗交界處最多可在短時間內打到 2 倍上限；要更平滑可改滑動視窗或 token bucket。
- `InMemoryStore` 不會清掉舊 IP（長時間執行會累積記憶體），也不支援多程序共享，正式環境要換 Redis。
- 全 0 卡號能通過 Luhn 檢查（有測試記錄此行為），沒做卡別 BIN 檢查。
- `RateLimiter` 沒有加鎖，多執行緒同時呼叫可能多放行幾次。
