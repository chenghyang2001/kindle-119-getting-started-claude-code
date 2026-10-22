import pytest

from pricing import calculate_total


def test_regular_total():
    assert calculate_total(100) == 100


def test_negative_subtotal_raises():
    with pytest.raises(ValueError):
        calculate_total(-1)
