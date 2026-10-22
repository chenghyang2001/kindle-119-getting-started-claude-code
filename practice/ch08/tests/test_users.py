import pytest

from users import create_user, get_user, reset_users


@pytest.fixture(autouse=True)
def _clean():
    reset_users()


def test_create_and_get_user():
    create_user("alice", "alice@example.com", "old-pass")
    assert get_user("alice")["email"] == "alice@example.com"


def test_get_missing_user_raises():
    with pytest.raises(LookupError):
        get_user("nobody")
