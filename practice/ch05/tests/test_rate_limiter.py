"""rate limiter 測試（TDD：先寫測試、確認紅燈，再實作）。"""
import pytest

from payments.rate_limiter import InMemoryStore, RateLimiter


class FakeClock:
    """可手動推進的假時鐘，避免測試真的等 60 秒。"""

    def __init__(self, start: float = 1_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def limiter(clock):
    return RateLimiter(limit=100, window_seconds=60, clock=clock, store=InMemoryStore())


def hit(limiter, ip, times):
    return [limiter.check(ip) for _ in range(times)]


def test_allows_first_100_requests(limiter):
    results = hit(limiter, "1.1.1.1", 100)
    assert all(r.allowed for r in results)
    assert all(r.status == 200 for r in results)


def test_remaining_counts_down(limiter):
    first, second = hit(limiter, "1.1.1.1", 2)
    assert first.remaining == 99
    assert second.remaining == 98


def test_101st_request_returns_429(limiter):
    hit(limiter, "1.1.1.1", 100)
    result = limiter.check("1.1.1.1")
    assert result.allowed is False
    assert result.status == 429
    assert result.remaining == 0


def test_retry_after_is_seconds_until_reset(limiter, clock):
    hit(limiter, "1.1.1.1", 100)
    clock.advance(20.5)
    result = limiter.check("1.1.1.1")
    assert result.headers["Retry-After"] == "40"  # 剩 39.5 秒，無條件進位


def test_retry_after_at_least_one_second(limiter, clock):
    hit(limiter, "1.1.1.1", 100)
    clock.advance(59.99)
    assert limiter.check("1.1.1.1").headers["Retry-After"] == "1"


def test_still_blocked_just_before_reset(limiter, clock):
    hit(limiter, "1.1.1.1", 100)
    clock.advance(59.9)
    assert limiter.check("1.1.1.1").allowed is False


def test_resets_after_60_seconds(limiter, clock):
    hit(limiter, "1.1.1.1", 100)
    clock.advance(60)
    result = limiter.check("1.1.1.1")
    assert result.allowed is True
    assert result.remaining == 99


def test_ips_are_independent(limiter):
    hit(limiter, "1.1.1.1", 100)
    assert limiter.check("1.1.1.1").allowed is False
    assert limiter.check("2.2.2.2").allowed is True


def test_whitelisted_ip_is_never_limited(clock):
    limiter = RateLimiter(
        limit=100, window_seconds=60, clock=clock, store=InMemoryStore(),
        whitelist={"10.0.0.1"},
    )
    results = hit(limiter, "10.0.0.1", 1000)
    assert all(r.allowed for r in results)
    assert limiter.check("8.8.8.8").allowed is True


def test_allowed_response_has_no_retry_after(limiter):
    assert "Retry-After" not in limiter.check("1.1.1.1").headers


@pytest.mark.parametrize("limit, window", [(0, 60), (100, 0), (-1, 60)])
def test_invalid_config(clock, limit, window):
    with pytest.raises(ValueError):
        RateLimiter(limit=limit, window_seconds=window, clock=clock)
