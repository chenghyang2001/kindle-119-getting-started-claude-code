"""calculate_discounted_price 的正常、邊界、例外測試。"""
import pytest

from utils.calculator import calculate_discounted_price


# 正常案例
@pytest.mark.parametrize("price, discount, code, expected", [
    (100, 0.2, None, 80.0),
    (100, 0.2, "VIP", 76.0),
    (200, 0.1, "staff", 162.0),   # 大小寫不敏感
    (19.99, 0.15, None, 16.99),
])
def test_normal(price, discount, code, expected):
    assert calculate_discounted_price(price, discount, code) == expected


def test_customer_code_none_is_same_as_omitted():
    assert calculate_discounted_price(100, 0.3, customer_code=None) == \
        calculate_discounted_price(100, 0.3) == 70.0


# 邊界案例
@pytest.mark.parametrize("price, discount, expected", [
    (0, 0.5, 0.0),
    (100, 0, 100.0),
    (100, 1, 0.0),
    (0.01, 0.5, 0.01),  # 0.005 四捨五入（浮點誤差下為 0.01）
])
def test_boundaries(price, discount, expected):
    assert calculate_discounted_price(price, discount) == expected


# 例外案例
@pytest.mark.parametrize("price, discount", [(-1, 0.1), (100, -0.1), (100, 1.01)])
def test_value_errors(price, discount):
    with pytest.raises(ValueError):
        calculate_discounted_price(price, discount)


@pytest.mark.parametrize("price, discount", [("100", 0.1), (100, None), (True, 0.1)])
def test_type_errors(price, discount):
    with pytest.raises(TypeError):
        calculate_discounted_price(price, discount)


def test_unknown_customer_code():
    with pytest.raises(ValueError, match="未知"):
        calculate_discounted_price(100, 0.1, "GOLD")


def test_customer_code_wrong_type():
    with pytest.raises(TypeError):
        calculate_discounted_price(100, 0.1, 123)
