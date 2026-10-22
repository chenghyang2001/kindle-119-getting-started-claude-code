"""密碼變更通知：載入 HTML 範本並透過 EmailService 寄出。"""
import html
from pathlib import Path
from string import Template

from email_service import EmailService

TEMPLATE_DIR = Path(__file__).parent / "templates"
PASSWORD_CHANGED_SUBJECT = "您的密碼已變更"


def render_password_changed(username: str, changed_at: str) -> str:
    template_text = (TEMPLATE_DIR / "password_changed.html").read_text(encoding="utf-8")
    # 使用者名稱來自外部輸入，先跳脫避免 HTML 注入
    return Template(template_text).substitute(
        username=html.escape(username), changed_at=html.escape(changed_at)
    )


def send_password_changed_email(service: EmailService, to: str, username: str, changed_at: str) -> bool:
    body = render_password_changed(username, changed_at)
    return service.send_email(to, PASSWORD_CHANGED_SUBJECT, body)
