"""processor 測試：閘道完全 mock，不碰外部服務。"""
from unittest.mock import create_autospec

import pytest

from payments.gateway import GatewayError, GatewayResponse, GatewayTimeout, PaymentGateway
from payments.processor import Payment, PaymentProcessor, PaymentStatus


@pytest.fixture
def gateway():
    return create_autospec(PaymentGateway, instance=True)


def make_payment(**overrides):
    fields = dict(
        card_number="4242424242424242", exp_month=12, exp_year=2099,
        cvv="123", amount_cents=50_000,
    )
    fields.update(overrides)
    return Payment(**fields)


def test_approved(gateway):
    gateway.charge.return_value = GatewayResponse(approved=True, transaction_id="tx_1")
    payment = PaymentProcessor(gateway).process(make_payment())
    assert payment.status is PaymentStatus.APPROVED
    assert payment.transaction_id == "tx_1"
    gateway.charge.assert_called_once_with("4242424242424242", 50_000, "TWD")


def test_declined_is_not_retried(gateway):
    gateway.charge.return_value = GatewayResponse(approved=False, decline_reason="insufficient_funds")
    payment = PaymentProcessor(gateway).process(make_payment())
    assert payment.status is PaymentStatus.DECLINED
    assert payment.failure_reason == "insufficient_funds"
    assert gateway.charge.call_count == 1


def test_timeout_then_success(gateway):
    gateway.charge.side_effect = [
        GatewayTimeout(), GatewayTimeout(), GatewayResponse(approved=True, transaction_id="tx_3"),
    ]
    payment = PaymentProcessor(gateway, max_retries=3).process(make_payment())
    assert payment.status is PaymentStatus.APPROVED
    assert payment.attempts == 3
    assert gateway.charge.call_count == 3


def test_timeout_exhausts_retries(gateway):
    gateway.charge.side_effect = GatewayTimeout()
    payment = PaymentProcessor(gateway, max_retries=3).process(make_payment())
    assert payment.status is PaymentStatus.FAILED
    assert payment.failure_reason == "gateway_timeout"
    assert gateway.charge.call_count == 3


def test_gateway_error_not_retried(gateway):
    gateway.charge.side_effect = GatewayError("500")
    payment = PaymentProcessor(gateway).process(make_payment())
    assert payment.status is PaymentStatus.FAILED
    assert payment.failure_reason.startswith("gateway_error")
    assert gateway.charge.call_count == 1


@pytest.mark.parametrize(
    "overrides, reason",
    [
        ({"card_number": "4242424242424241"}, "invalid_card_number"),
        ({"exp_month": 1, "exp_year": 2020}, "card_expired"),
        ({"cvv": "12"}, "invalid_cvv"),
        ({"amount_cents": 0}, "invalid_amount"),
        ({"amount_cents": -100}, "invalid_amount"),
    ],
)
def test_invalid_input_never_hits_gateway(gateway, overrides, reason):
    payment = PaymentProcessor(gateway).process(make_payment(**overrides))
    assert payment.status is PaymentStatus.FAILED
    assert payment.failure_reason == reason
    gateway.charge.assert_not_called()


def test_cannot_reprocess_non_pending(gateway):
    payment = make_payment(status=PaymentStatus.APPROVED)
    with pytest.raises(ValueError):
        PaymentProcessor(gateway).process(payment)
    gateway.charge.assert_not_called()


def test_max_retries_must_be_positive(gateway):
    with pytest.raises(ValueError):
        PaymentProcessor(gateway, max_retries=0)
