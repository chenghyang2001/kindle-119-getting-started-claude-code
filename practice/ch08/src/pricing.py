"""訂單價格計算。"""


def calculate_total(subtotal: float, customer_type: str = "regular") -> float:
    if subtotal < 0:
        raise ValueError("小計不可為負數")
    total = subtotal
    return round(total, 2)
