from datetime import date

import pytest

from billing.proration import days_in_month, prorate, upgrade_credit


def test_days_in_month():
    assert days_in_month(date(2024, 2, 10)) == 29
    assert days_in_month(date(2023, 12, 1)) == 31


def test_full_month():
    assert prorate(30.00, date(2024, 4, 1)) == 30.00


def test_partial_month_rounding():
    # 49.00 * 29/31 = 45.8387... -> 45.84
    assert prorate(49.00, date(2024, 1, 3)) == 45.84


def test_bad_range():
    with pytest.raises(ValueError):
        prorate(10, date(2024, 1, 10), date(2024, 1, 5))


def test_negative_price():
    with pytest.raises(ValueError):
        prorate(-1, date(2024, 1, 1))


def test_upgrade_credit():
    assert upgrade_credit(30.00, 60.00, date(2024, 4, 16)) == 15.00
