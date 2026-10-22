"""付款流程：驗證卡片 → 呼叫閘道（逾時重試）→ 更新 Payment 狀態。"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from payments.gateway import GatewayError, GatewayTimeout, PaymentGateway
from payments.validators import is_valid_card_number, is_valid_cvv, is_valid_expiry


class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    FAILED = "failed"


@dataclass
class Payment:
    card_number: str
    exp_month: int
    exp_year: int
    cvv: str
    amount_cents: int
    currency: str = "TWD"
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: str | None = None
    failure_reason: str | None = None
    attempts: int = field(default=0)


class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway, max_retries: int = 3) -> None:
        if max_retries < 1:
            raise ValueError("max_retries 至少為 1")
        self.gateway = gateway
        self.max_retries = max_retries

    def process(self, payment: Payment) -> Payment:
        if payment.status is not PaymentStatus.PENDING:
            raise ValueError(f"只能處理 pending 付款，目前狀態：{payment.status.value}")
        invalid_reason = self._validate(payment)
        if invalid_reason:
            return self._fail(payment, invalid_reason)
        return self._charge_with_retry(payment)

    def _validate(self, payment: Payment) -> str | None:
        if payment.amount_cents <= 0:
            return "invalid_amount"
        if not is_valid_card_number(payment.card_number):
            return "invalid_card_number"
        if not is_valid_expiry(payment.exp_month, payment.exp_year):
            return "card_expired"
        if not is_valid_cvv(payment.cvv, payment.card_number):
            return "invalid_cvv"
        return None

    def _charge_with_retry(self, payment: Payment) -> Payment:
        # 只有逾時才重試；明確拒絕或閘道錯誤重試也不會變好
        while payment.attempts < self.max_retries:
            payment.attempts += 1
            try:
                response = self.gateway.charge(
                    payment.card_number, payment.amount_cents, payment.currency
                )
            except GatewayTimeout:
                continue
            except GatewayError as exc:
                return self._fail(payment, f"gateway_error: {exc}")
            if response.approved:
                payment.status = PaymentStatus.APPROVED
                payment.transaction_id = response.transaction_id
            else:
                payment.status = PaymentStatus.DECLINED
                payment.failure_reason = response.decline_reason
            return payment
        return self._fail(payment, "gateway_timeout")

    @staticmethod
    def _fail(payment: Payment, reason: str) -> Payment:
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = reason
        return payment
