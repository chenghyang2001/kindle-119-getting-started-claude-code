"""/api/quote 端點與速率限制測試。"""
import pytest

from app import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def test_quote_ok(client):
    resp = client.post("/api/quote", json={"price": 100, "discount": 0.2, "customer_code": "VIP"})
    assert resp.status_code == 200
    assert resp.get_json()["final_price"] == 76.0


def test_quote_bad_input(client):
    resp = client.post("/api/quote", json={"price": 100})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "bad_request"


def test_rate_limit_11th_request_is_429(client):
    for i in range(10):
        resp = client.get("/api/quote?price=100&discount=0.1")
        assert resp.status_code == 200, f"第 {i + 1} 次不應被擋"
    resp = client.get("/api/quote?price=100&discount=0.1")
    assert resp.status_code == 429
    assert resp.is_json
    assert resp.get_json()["error"] == "too_many_requests"


def test_rate_limit_is_per_ip(client):
    for _ in range(10):
        client.get("/api/quote?price=1&discount=0", environ_base={"REMOTE_ADDR": "10.0.0.1"})
    resp = client.get("/api/quote?price=1&discount=0", environ_base={"REMOTE_ADDR": "10.0.0.2"})
    assert resp.status_code == 200
