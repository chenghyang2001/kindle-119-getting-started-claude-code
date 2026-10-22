"""付款閘道介面。真實環境會呼叫外部 API；測試時一律以 mock 取代。"""
from __future__ import annotations

from dataclasses import dataclass


class GatewayTimeout(Exception):
    """閘道逾時（可重試）。"""


class GatewayError(Exception):
    """閘道回傳非預期錯誤（不可重試）。"""


@dataclass(frozen=True)
class GatewayResponse:
    approved: bool
    transaction_id: str | None = None
    decline_reason: str | None = None


class PaymentGateway:
    """外部付款閘道的薄包裝。"""

    def __init__(self, api_url: str, api_key: str) -> None:
        self.api_url = api_url
        self.api_key = api_key

    def charge(self, card_number: str, amount_cents: int, currency: str) -> GatewayResponse:
        # 練習專案不真的連線，避免測試意外打到外部服務
        raise NotImplementedError("請在測試中以 mock 取代 PaymentGateway")
