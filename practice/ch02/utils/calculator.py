"""折扣價格計算工具。"""

# 會員代碼對應的額外折扣率（在一般折扣之後再套用）
CUSTOMER_EXTRA_DISCOUNTS = {
    "VIP": 0.05,
    "STAFF": 0.10,
}


def _validate_number(name, value):
    """確認數值型別；bool 是 int 的子類別，要特別排除。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} 必須是數字，收到 {type(value).__name__}")


def calculate_discounted_price(price, discount, customer_code=None):
    """計算套用折扣後的價格。

    參數:
        price: 原價，必須是 >= 0 的數字。
        discount: 折扣率，介於 0 到 1 之間（0.2 代表打八折）。
        customer_code: 會員代碼（可省略）。"VIP" 再減 5%、"STAFF" 再減 10%；
            None 表示一般客戶，不另外打折。

    回傳:
        折扣後價格，四捨五入到小數第 2 位。

    例外:
        TypeError: price 或 discount 不是數字，或 customer_code 不是字串。
        ValueError: price 為負、discount 超出 0~1，或 customer_code 不存在。

    範例:
        >>> calculate_discounted_price(100, 0.2)
        80.0
        >>> calculate_discounted_price(100, 0.2, "VIP")
        76.0
    """
    _validate_number("price", price)
    _validate_number("discount", discount)
    if price < 0:
        raise ValueError("price 不可為負數")
    if not 0 <= discount <= 1:
        raise ValueError("discount 必須介於 0 到 1 之間")

    final_price = price * (1 - discount)

    if customer_code is not None:
        if not isinstance(customer_code, str):
            raise TypeError("customer_code 必須是字串或 None")
        code = customer_code.strip().upper()
        if code not in CUSTOMER_EXTRA_DISCOUNTS:
            raise ValueError(f"未知的 customer_code：{customer_code}")
        final_price *= 1 - CUSTOMER_EXTRA_DISCOUNTS[code]

    return round(final_price, 2)
