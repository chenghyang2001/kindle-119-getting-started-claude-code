"""Email 服務：預設使用模擬的 SendGrid 用戶端，不會真的寄信。"""
from dataclasses import dataclass, field


class EmailSendError(Exception):
    """寄信失敗（SendGrid 回非 2xx 或連線錯誤）。"""


@dataclass
class MockSendGridClient:
    """模擬 SendGrid API；把寄出的信存在 sent 清單供測試檢查。"""

    sent: list[dict] = field(default_factory=list)
    should_fail: bool = False

    def send(self, to: str, subject: str, html: str) -> int:
        if self.should_fail:
            raise EmailSendError("SendGrid 模擬失敗")
        self.sent.append({"to": to, "subject": subject, "html": html})
        return 202  # SendGrid 成功時回 202 Accepted


class EmailService:
    """寄信服務；DEFAULT_SENDER 為預設寄件者。"""

    DEFAULT_SENDER = "no-reply@example.com"

    def __init__(self, client: MockSendGridClient | None = None):
        self.client = client if client is not None else MockSendGridClient()

    def send_email(self, to: str, subject: str, html: str) -> bool:
        if not to or "@" not in to:
            raise ValueError(f"收件者 email 格式錯誤：{to!r}")
        return self.client.send(to, subject, html) == 202
