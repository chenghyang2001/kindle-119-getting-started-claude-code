"""validators 的參數化測試。"""
from datetime import date

import pytest

from payments.validators import is_valid_card_number, is_valid_cvv, is_valid_expiry

TODAY = date(2026, 10, 22)


@pytest.mark.parametrize(
    "number, expected",
    [
        ("4242424242424242", True),  # Visa 測試卡
        ("5555555555554444", True),  # MasterCard
        ("378282246310005", True),  # Amex 15 位
        ("4242 4242 4242 4242", True),  # 含空白
        ("4242-4242-4242-4242", True),  # 含連字號
        ("4222222222222", True),  # 13 位下限
        ("4242424242424241", False),  # 末碼錯 → Luhn 失敗
        ("", False),
        (None, False),
        ("4242abcd42424242", False),
        ("424242424242", False),  # 12 位太短
        ("42424242424242424242", False),  # 20 位太長
    ],
)
def test_card_number(number, expected):
    assert is_valid_card_number(number) is expected


def test_card_number_19_digits_upper_bound():
    assert is_valid_card_number("4242424242424242428") is True  # 19 位上限且 Luhn 正確
    assert is_valid_card_number("4242424242424242429") is False  # 19 位但 Luhn 錯


def test_all_zero_passes_luhn_format_check():
    # 全 0 的 Luhn 總和為 0，格式上算合法；是否拒絕交給閘道（記錄在 NOTES 的已知限制）
    assert is_valid_card_number("0" * 16) is True


@pytest.mark.parametrize(
    "month, year, expected",
    [
        (12, 2027, True),
        (10, 2026, True),  # 本月仍有效
        (9, 2026, False),  # 上個月過期
        (1, 2027, True),  # 跨年
        (12, 2025, False),
        (10, 26, True),  # 兩位數年份
        (0, 2027, False),
        (13, 2027, False),
        ("10", 2027, False),  # 非 int
    ],
)
def test_expiry(month, year, expected):
    assert is_valid_expiry(month, year, today=TODAY) is expected


@pytest.mark.parametrize(
    "cvv, card, expected",
    [
        ("123", "4242424242424242", True),
        ("1234", "4242424242424242", False),
        ("1234", "378282246310005", True),  # Amex 4 位
        ("123", "378282246310005", False),
        ("12a", "4242424242424242", False),
        ("", "4242424242424242", False),
        (None, "4242424242424242", False),
        ("123", None, True),  # 不知道卡別時預設 3 位
    ],
)
def test_cvv(cvv, card, expected):
    assert is_valid_cvv(cvv, card) is expected
