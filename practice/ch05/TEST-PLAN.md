# 測試計畫（TEST-PLAN）

先列功能與關鍵邊界，再寫測試（K119 第 5 章：讓 AI 先想清楚「要測什麼」）。

## 1. validators.py

| 功能 | 正常 | 關鍵邊界 / 錯誤 |
| --- | --- | --- |
| `is_valid_card_number` | Visa / MasterCard / Amex 測試卡號通過 | 末碼錯一位（Luhn 失敗）、空字串、None、含字母、12 位（太短）、20 位（太長）、13 位與 19 位剛好合法、含空白或連字號、全 0 |
| `is_valid_expiry` | 未來月份通過 | 本月（仍有效）、上個月（過期）、month=0 / 13、兩位數年份、跨年 12 月→1 月、非 int |
| `is_valid_cvv` | 一般卡 3 位 | Amex 須 4 位、一般卡給 4 位失敗、Amex 給 3 位失敗、含字母、空字串、None |

## 2. processor.py（閘道全部 mock）

| 情境 | 預期 Payment 狀態 | 閘道呼叫次數 |
| --- | --- | --- |
| 閘道核准 | APPROVED，帶 transaction_id | 1 |
| 閘道拒絕（餘額不足） | DECLINED，帶 decline_reason | 1（拒絕不重試） |
| 前兩次逾時、第三次核准 | APPROVED，attempts=3 | 3 |
| 一直逾時 | FAILED，reason=gateway_timeout | = max_retries |
| 閘道錯誤 | FAILED，不重試 | 1 |
| 卡號 / 到期 / CVV / 金額不合法 | FAILED，對應 reason | 0（不可打到閘道） |
| 處理非 pending 付款 | 拋 ValueError | 0 |
| max_retries < 1 | 建構時拋 ValueError | — |

## 3. rate_limiter.py（TDD：先寫測試，確認紅燈）

| 規則 | 測試 |
| --- | --- |
| 每 IP 每分鐘 100 次 | 第 1～100 次允許、第 101 次拒絕 |
| 超限回 429 + Retry-After | status=429，Retry-After 為距離視窗重置的秒數（無條件進位、至少 1） |
| 60 秒重置 | 第 59.9 秒仍拒絕，第 60 秒恢復允許 |
| 不同 IP 互不影響 | A 用完，B 仍允許 |
| 白名單 | 白名單 IP 打 1000 次都允許 |
| 允許時回 200 + 剩餘次數 | remaining 由 99 遞減 |
| 參數檢查 | limit / window ≤ 0 拋 ValueError |

儲存用記憶體 dict 取代 Redis；時間由可注入的 `clock` 函式提供，測試用假時鐘控制，不用 `sleep`。
