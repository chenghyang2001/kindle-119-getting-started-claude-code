"""每 IP 固定視窗限流器。

書上範例用 Redis（INCR + EXPIRE）；這裡用記憶體 dict 取代，
介面刻意對齊 Redis 的「取值／寫值」，之後換成 Redis 只需替換 store。
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable, Iterable


@dataclass
class WindowState:
    window_start: float
    count: int


class InMemoryStore:
    """取代 Redis 的記憶體儲存（單一程序內有效，不跨程序共享）。"""

    def __init__(self) -> None:
        self._data: dict[str, WindowState] = {}

    def get(self, key: str) -> WindowState | None:
        return self._data.get(key)

    def set(self, key: str, state: WindowState) -> None:
        self._data[key] = state


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    status: int
    remaining: int
    headers: dict[str, str] = field(default_factory=dict)


class RateLimiter:
    def __init__(
        self,
        limit: int = 100,
        window_seconds: float = 60,
        clock: Callable[[], float] = time.monotonic,
        store: InMemoryStore | None = None,
        whitelist: Iterable[str] = (),
    ) -> None:
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit 與 window_seconds 必須大於 0")
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self.store = store if store is not None else InMemoryStore()
        self.whitelist = frozenset(whitelist)

    def check(self, ip: str) -> RateLimitResult:
        if ip in self.whitelist:
            return RateLimitResult(allowed=True, status=200, remaining=self.limit)

        now = self.clock()
        state = self.store.get(ip)
        if state is None or now - state.window_start >= self.window_seconds:
            state = WindowState(window_start=now, count=0)

        if state.count >= self.limit:
            reset_in = state.window_start + self.window_seconds - now
            retry_after = max(1, math.ceil(reset_in))
            return RateLimitResult(
                allowed=False, status=429, remaining=0,
                headers={"Retry-After": str(retry_after)},
            )

        state.count += 1
        self.store.set(ip, state)
        return RateLimitResult(allowed=True, status=200, remaining=self.limit - state.count)
