"""交易式訂單處理：照 K119 第 10 章的精確 6 步驟實作 process_pending_orders()。

書上的 6 步驟：
1. 從 orders table 取出所有 status 為 'pending' 的訂單
2. 每筆訂單呼叫 inventory.check_availability(product_id, quantity) 確認庫存
3. 有庫存：inventory.reserve(product_id, quantity)，訂單改為 'processing'
4. warehouse.create_delivery_note(order_id) 產生出貨單號
5. warehouse.notify(delivery_note_id) 通知倉庫
6. 沒庫存：訂單維持 'pending' 並記錄 warning
交易約束：任何一步失敗，回滾訂單與庫存的變更。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass
class Order:
    id: int
    product_id: str
    quantity: int
    status: str = "pending"


@dataclass
class OrdersTable:
    """示範用的記憶體 orders table。"""

    rows: dict[int, Order] = field(default_factory=dict)

    def find_by_status(self, status: str) -> list[Order]:
        return [o for o in self.rows.values() if o.status == status]

    def update_status(self, order_id: int, status: str) -> None:
        self.rows[order_id].status = status


class Inventory(Protocol):
    def check_availability(self, product_id: str, quantity: int) -> bool: ...
    def reserve(self, product_id: str, quantity: int) -> None: ...
    def release(self, product_id: str, quantity: int) -> None: ...


class Warehouse(Protocol):
    def create_delivery_note(self, order_id: int) -> str: ...
    def notify(self, delivery_note_id: str) -> None: ...


@dataclass
class _UndoLog:
    """記錄本次執行做過的變更，失敗時反向撤銷。"""

    statuses: list[tuple[int, str]] = field(default_factory=list)
    reservations: list[tuple[str, int]] = field(default_factory=list)
    delivery_notes: list[str] = field(default_factory=list)


def _rollback(orders: OrdersTable, inventory: Inventory, warehouse: Warehouse, undo: _UndoLog) -> None:
    """反向順序撤銷；個別撤銷失敗只記 log，繼續撤銷其他項目，避免半套回滾。"""
    for order_id, old_status in reversed(undo.statuses):
        orders.update_status(order_id, old_status)
    for product_id, quantity in reversed(undo.reservations):
        try:
            inventory.release(product_id, quantity)
        except Exception:  # noqa: BLE001 - 回滾階段不能讓單一失敗中斷整個回滾
            logger.exception("回滾時釋放庫存失敗：%s x%s", product_id, quantity)
    # 書上只要求回滾訂單與庫存；出貨單是外部系統，有提供取消介面才做補償
    cancel = getattr(warehouse, "cancel_delivery_note", None)
    if callable(cancel):
        for note_id in reversed(undo.delivery_notes):
            try:
                cancel(note_id)
            except Exception:  # noqa: BLE001
                logger.exception("回滾時取消出貨單失敗：%s", note_id)


def _process_one(order: Order, orders: OrdersTable, inventory: Inventory,
                 warehouse: Warehouse, undo: _UndoLog) -> bool:
    """處理單筆訂單（步驟 2–6），回傳是否已進入 processing。"""
    if not inventory.check_availability(order.product_id, order.quantity):  # 步驟 2
        logger.warning("訂單 %s 庫存不足，維持 pending", order.id)  # 步驟 6
        return False
    inventory.reserve(order.product_id, order.quantity)  # 步驟 3
    undo.reservations.append((order.product_id, order.quantity))
    undo.statuses.append((order.id, order.status))
    orders.update_status(order.id, "processing")
    note_id = warehouse.create_delivery_note(order.id)  # 步驟 4
    undo.delivery_notes.append(note_id)
    warehouse.notify(note_id)  # 步驟 5
    return True


def process_pending_orders(orders: OrdersTable, inventory: Inventory, warehouse: Warehouse) -> list[int]:
    """處理所有 pending 訂單；整批是一個交易，任何一步失敗就全部回滾並重新拋出例外。

    回傳成功進入 processing 的訂單 id 清單。
    """
    pending = orders.find_by_status("pending")  # 步驟 1
    undo = _UndoLog()
    processed: list[int] = []
    try:
        for order in pending:
            if _process_one(order, orders, inventory, warehouse, undo):
                processed.append(order.id)
    except Exception:
        logger.error("訂單處理失敗，回滾本次所有變更")
        _rollback(orders, inventory, warehouse, undo)
        raise
    return processed
