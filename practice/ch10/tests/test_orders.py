"""process_pending_orders() 測試：正常流程 + 每一步失敗都會回滾。"""

import logging

import pytest

from src.orders import Order, OrdersTable, process_pending_orders


class Boom(RuntimeError):
    """測試注入的失敗。"""


class FakeInventory:
    def __init__(self, stock, fail_on=None, fail_at_call=1):
        self.stock = dict(stock)
        self.fail_on = fail_on  # 要失敗的方法名稱
        self.fail_at_call = fail_at_call  # 第幾次呼叫時失敗
        self.calls = {}

    def _maybe_fail(self, name):
        self.calls[name] = self.calls.get(name, 0) + 1
        if self.fail_on == name and self.calls[name] == self.fail_at_call:
            raise Boom(name)

    def check_availability(self, product_id, quantity):
        self._maybe_fail("check_availability")
        return self.stock.get(product_id, 0) >= quantity

    def reserve(self, product_id, quantity):
        self._maybe_fail("reserve")
        self.stock[product_id] -= quantity

    def release(self, product_id, quantity):
        self.stock[product_id] += quantity


class FakeWarehouse:
    def __init__(self, fail_on=None, fail_at_call=1):
        self.fail_on = fail_on
        self.fail_at_call = fail_at_call
        self.calls = {}
        self.notes = []
        self.notified = []
        self.cancelled = []

    def _maybe_fail(self, name):
        self.calls[name] = self.calls.get(name, 0) + 1
        if self.fail_on == name and self.calls[name] == self.fail_at_call:
            raise Boom(name)

    def create_delivery_note(self, order_id):
        self._maybe_fail("create_delivery_note")
        note = f"DN-{order_id}"
        self.notes.append(note)
        return note

    def notify(self, delivery_note_id):
        self._maybe_fail("notify")
        self.notified.append(delivery_note_id)

    def cancel_delivery_note(self, note_id):
        self.cancelled.append(note_id)


class FailingOrdersTable(OrdersTable):
    """可讓步驟 1（查詢）或狀態更新失敗的 orders table。"""

    def __init__(self, rows, fail_find=False, fail_update_for=None):
        super().__init__(rows)
        self.fail_find = fail_find
        self.fail_update_for = fail_update_for

    def find_by_status(self, status):
        if self.fail_find:
            raise Boom("find_by_status")
        return super().find_by_status(status)

    def update_status(self, order_id, status):
        if order_id == self.fail_update_for and status == "processing":
            raise Boom("update_status")
        super().update_status(order_id, status)


STOCK = {"A": 10, "B": 10}


def make_rows():
    # 訂單 1、2 都有庫存；第二筆失敗時要連第一筆一起回滾
    return {1: Order(1, "A", 3), 2: Order(2, "B", 4)}


def snapshot(table):
    return {oid: o.status for oid, o in table.rows.items()}


def test_happy_path_processes_all():
    orders, inv, wh = OrdersTable(make_rows()), FakeInventory(STOCK), FakeWarehouse()
    assert process_pending_orders(orders, inv, wh) == [1, 2]
    assert snapshot(orders) == {1: "processing", 2: "processing"}
    assert inv.stock == {"A": 7, "B": 6}
    assert wh.notified == ["DN-1", "DN-2"]


def test_no_stock_stays_pending_and_warns(caplog):
    rows = {1: Order(1, "A", 3), 2: Order(2, "B", 99)}
    orders, inv, wh = OrdersTable(rows), FakeInventory(STOCK), FakeWarehouse()
    with caplog.at_level(logging.WARNING):
        assert process_pending_orders(orders, inv, wh) == [1]
    assert snapshot(orders) == {1: "processing", 2: "pending"}
    assert inv.stock["B"] == 10
    assert "庫存不足" in caplog.text


def test_only_pending_orders_are_touched():
    rows = {1: Order(1, "A", 3, status="shipped"), 2: Order(2, "B", 4)}
    orders, inv, wh = OrdersTable(rows), FakeInventory(STOCK), FakeWarehouse()
    assert process_pending_orders(orders, inv, wh) == [2]
    assert snapshot(orders) == {1: "shipped", 2: "processing"}


def test_step1_fetch_failure_changes_nothing():
    orders = FailingOrdersTable(make_rows(), fail_find=True)
    inv, wh = FakeInventory(STOCK), FakeWarehouse()
    with pytest.raises(Boom):
        process_pending_orders(orders, inv, wh)
    assert snapshot(orders) == {1: "pending", 2: "pending"}
    assert inv.stock == STOCK


# 步驟 2～5 各自在「第二筆訂單」失敗，驗證第一筆已做的變更也被回滾
@pytest.mark.parametrize("target, method", [
    ("inventory", "check_availability"),    # 步驟 2
    ("inventory", "reserve"),               # 步驟 3（保留庫存）
    ("orders", "update_status"),            # 步驟 3（改 processing）
    ("warehouse", "create_delivery_note"),  # 步驟 4
    ("warehouse", "notify"),                # 步驟 5
])
def test_each_step_failure_rolls_back(target, method):
    if target == "orders":
        orders = FailingOrdersTable(make_rows(), fail_update_for=2)
        inv, wh = FakeInventory(STOCK), FakeWarehouse()
    else:
        orders = OrdersTable(make_rows())
        inv = FakeInventory(STOCK, fail_on=method if target == "inventory" else None, fail_at_call=2)
        wh = FakeWarehouse(fail_on=method if target == "warehouse" else None, fail_at_call=2)

    with pytest.raises(Boom):
        process_pending_orders(orders, inv, wh)

    assert snapshot(orders) == {1: "pending", 2: "pending"}, "訂單狀態未回滾"
    assert inv.stock == STOCK, "庫存未回滾"
    assert sorted(wh.cancelled) == sorted(wh.notes), "已建立的出貨單未補償取消"


def test_failure_on_first_order_rolls_back():
    orders = OrdersTable(make_rows())
    inv, wh = FakeInventory(STOCK), FakeWarehouse(fail_on="notify", fail_at_call=1)
    with pytest.raises(Boom):
        process_pending_orders(orders, inv, wh)
    assert snapshot(orders) == {1: "pending", 2: "pending"}
    assert inv.stock == STOCK
    assert wh.cancelled == ["DN-1"]


def test_empty_orders_table():
    assert process_pending_orders(OrdersTable(), FakeInventory(STOCK), FakeWarehouse()) == []
