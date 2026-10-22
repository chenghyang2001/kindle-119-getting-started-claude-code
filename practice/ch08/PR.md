# feat: 密碼變更後寄送通知信

分支：`feature/password-change-notifications` → `main`（練習用，未 push、未開 PR）

## 做了什麼

- **Email 服務**（`src/email_service.py`）：`EmailService` 包一層 SendGrid 用戶端；預設用 `MockSendGridClient`，不會真的寄信，寄出的信存在 `client.sent` 供測試檢查。可設 `should_fail=True` 模擬寄信失敗。
- **HTML 範本**（`src/templates/password_changed.html` + `src/notifications.py`）：用 `string.Template` 填入使用者名稱與變更時間，填入前先 `html.escape`，避免使用者名稱夾帶 HTML。
- **`change_password` 整合**（`src/users.py`）：驗證舊密碼、新密碼至少 8 字元，更新後寄通知信。
- **測試**（`tests/test_password_notifications.py`）：成功寄信、舊密碼錯不寄信、新密碼太短被拒、寄信失敗仍保留新密碼、範本跳脫 HTML，共 5 個。
- 小重構：抽出 `PASSWORD_CHANGED_SUBJECT`、`DEFAULT_SENDER` 常數。

## 怎麼手動測

```bash
uv sync
uv run pytest -q          # 預期 9 passed

PYTHONUTF8=1 uv run python -c "
import sys; sys.path.insert(0, 'src')
from users import create_user, change_password
from email_service import EmailService, MockSendGridClient
c = MockSendGridClient(); create_user('alice', 'alice@example.com', 'old-pass')
print(change_password('alice', 'old-pass', 'new-pass-123', EmailService(c)))
print(c.sent[0]['to'], c.sent[0]['subject'])
"
# 預期輸出：
# True
# alice@example.com 您的密碼已變更
```

再試一次把舊密碼打錯，應拋出 `PermissionError`，且 `c.sent` 不會多一封信。

## 設計決策

1. **寄信失敗不回滾密碼**：密碼已經改了，通知只是盡力而為；回滾反而會讓使用者以為改成功卻登不進去。失敗時印警告並回傳 `False`，呼叫端可決定是否重試。
2. **用依賴注入傳入 email 服務**：`change_password(..., email_service=None)`，測試直接塞 mock；正式環境換成真的 SendGrid 用戶端即可，不用改業務邏輯。
3. **先驗證、後寄信**：舊密碼錯或新密碼不合格時直接拋錯，不會寄出任何信。
4. **範本用標準庫 `string.Template`**：功能夠用、不必加 Jinja2 依賴。
5. **通知信不含新密碼或重設連結**，只告知「已變更」與客服聯絡方式，降低信件外洩的風險。

## 未處理（後續可做）

- 真正的 SendGrid 用戶端與 API key 設定（應從環境變數讀取）。
- 寄信失敗的重試佇列。
- 密碼雜湊目前用 SHA-256（練習用），正式環境應改 bcrypt / argon2。
