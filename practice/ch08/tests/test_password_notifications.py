import pytest

from email_service import EmailService, MockSendGridClient
from notifications import render_password_changed
from users import _hash, change_password, create_user, get_user, reset_users


@pytest.fixture(autouse=True)
def _clean():
    reset_users()


@pytest.fixture
def client():
    return MockSendGridClient()


def test_change_password_sends_email(client):
    create_user("alice", "alice@example.com", "old-pass")
    assert change_password("alice", "old-pass", "new-pass-123", EmailService(client)) is True
    assert get_user("alice")["password_hash"] == _hash("new-pass-123")
    assert len(client.sent) == 1
    assert client.sent[0]["to"] == "alice@example.com"
    assert "alice" in client.sent[0]["html"]


def test_wrong_old_password_sends_nothing(client):
    create_user("bob", "bob@example.com", "secret-1")
    with pytest.raises(PermissionError):
        change_password("bob", "wrong", "new-pass-123", EmailService(client))
    assert client.sent == []


def test_short_new_password_rejected(client):
    create_user("carol", "carol@example.com", "secret-1")
    with pytest.raises(ValueError):
        change_password("carol", "secret-1", "short", EmailService(client))


def test_email_failure_keeps_new_password():
    create_user("dave", "dave@example.com", "secret-1")
    failing = MockSendGridClient(should_fail=True)
    assert change_password("dave", "secret-1", "new-pass-123", EmailService(failing)) is False
    assert get_user("dave")["password_hash"] == _hash("new-pass-123")


def test_template_escapes_html():
    body = render_password_changed("<script>x</script>", "2026-10-22")
    assert "<script>x</script>" not in body
    assert "&lt;script&gt;" in body
