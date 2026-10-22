"""訂閱費按比例計費（proration）工具。

金額一律以 ``Decimal`` 計算並以四捨五入（ROUND_HALF_UP）取到小數兩位，
避免 float 誤差與無條件捨去造成少收一分錢。
"""
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def days_in_month(d):
    """計算指定日期所在月份的天數。

    Args:
        d (datetime.date): 該月份中的任一天。

    Returns:
        int: 該月份的天數（28～31，會處理閏年）。

    Example:
        >>> days_in_month(date(2024, 2, 10))
        29
    """
    if d.month == 12:
        nxt = date(d.year + 1, 1, 1)
    else:
        nxt = date(d.year, d.month + 1, 1)
    return (nxt - date(d.year, d.month, 1)).days


def prorate(price, start, end=None):
    """依當月實際使用天數計算按比例的金額。

    計算公式為 ``price * 使用天數 / 當月天數``，起訖日都算在內，
    結果以四捨五入取到小數兩位。

    Args:
        price (float | int | Decimal): 整月的訂閱價格，必須 >= 0。
        start (datetime.date): 開始計費日（含）。
        end (datetime.date | None): 結束計費日（含）。省略時為該月最後一天。

    Returns:
        float: 按比例計算後的金額，取到小數兩位。

    Raises:
        ValueError: ``price`` 為負數，或 ``end`` 早於 ``start``、跨月份／年份。

    Example:
        >>> prorate(49.00, date(2024, 1, 3))  # 49 * 29 / 31 = 45.8387...
        45.84
    """
    if price < 0:
        raise ValueError("price must be >= 0")
    total = days_in_month(start)
    if end is None:
        end = date(start.year, start.month, total)
    if end < start or end.month != start.month or end.year != start.year:
        raise ValueError("bad range")
    used = (end - start).days + 1
    # 用 str() 轉 Decimal，避免把 float 的二進位誤差一起帶進來
    amount = Decimal(str(price)) * used / total
    return float(amount.quantize(CENT, rounding=ROUND_HALF_UP))


def upgrade_credit(old_price, new_price, change_day):
    """計算月中變更方案時需補收（或退還）的差額。

    Args:
        old_price (float): 舊方案整月價格。
        new_price (float): 新方案整月價格。
        change_day (datetime.date): 變更生效日，從這天起到月底改用新方案。

    Returns:
        float: 新方案剩餘天數費用減去舊方案剩餘天數費用；
        正數代表要補收，負數代表要退還。

    Raises:
        ValueError: 價格為負數時（由 :func:`prorate` 拋出）。

    Example:
        >>> upgrade_credit(30.00, 60.00, date(2024, 4, 16))
        15.0
    """
    left = Decimal(str(prorate(old_price, change_day)))
    charge = Decimal(str(prorate(new_price, change_day)))
    return float(charge - left)
