"""卡片資料驗證：Luhn 卡號、到期日、CVV。"""
from __future__ import annotations

from datetime import date


def is_valid_card_number(number: str | None) -> bool:
    """Luhn 檢查；允許空白與連字號分隔，長度須為 13～19 位數字。"""
    if number is None:
        return False
    digits = number.replace(" ", "").replace("-", "")
    if not digits.isdigit() or not 13 <= len(digits) <= 19:
        return False
    total = 0
    # 從最右邊數來，偶數位（第 2、4…位）乘 2，超過 9 減 9
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def is_valid_expiry(month: int, year: int, today: date | None = None) -> bool:
    """到期日有效到該月最後一天；year 接受兩位數（自動補 2000）。"""
    if not isinstance(month, int) or not isinstance(year, int):
        return False
    if not 1 <= month <= 12:
        return False
    if 0 <= year < 100:
        year += 2000
    today = today or date.today()
    return (year, month) >= (today.year, today.month)


def is_valid_cvv(cvv: str | None, card_number: str | None = None) -> bool:
    """CVV 為 3 位數；American Express（34/37 開頭）為 4 位數。"""
    if cvv is None or not cvv.isdigit():
        return False
    digits = (card_number or "").replace(" ", "").replace("-", "")
    expected_length = 4 if digits[:2] in ("34", "37") else 3
    return len(cvv) == expected_length
