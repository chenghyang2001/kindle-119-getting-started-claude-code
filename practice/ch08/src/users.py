"""使用者帳號模組（練習用的記憶體內資料庫）。"""
import hashlib

_USERS: dict[str, dict] = {}


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username: str, email: str, password: str) -> dict:
    if username in _USERS:
        raise ValueError(f"使用者已存在：{username}")
    _USERS[username] = {"username": username, "email": email, "password_hash": _hash(password)}
    return _USERS[username]


def get_user(username: str) -> dict:
    try:
        return _USERS[username]
    except KeyError:
        raise LookupError(f"找不到使用者：{username}") from None


def reset_users() -> None:
    """測試用：清空資料。"""
    _USERS.clear()


def change_password(username: str, old_password: str, new_password: str, email_service=None) -> bool:
    """變更密碼；成功後寄通知信。寄信失敗不回滾密碼變更（通知是盡力而為）。"""
    from datetime import datetime, timezone

    from email_service import EmailSendError, EmailService
    from notifications import send_password_changed_email

    user = get_user(username)
    if user["password_hash"] != _hash(old_password):
        raise PermissionError("舊密碼錯誤")
    if len(new_password) < 8:
        raise ValueError("新密碼至少需要 8 個字元")
    user["password_hash"] = _hash(new_password)

    service = email_service if email_service is not None else EmailService()
    changed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        send_password_changed_email(service, user["email"], username, changed_at)
    except (EmailSendError, ValueError) as exc:
        print(f"警告：密碼變更通知寄送失敗：{exc}")
        return False
    return True
