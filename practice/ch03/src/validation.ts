import { Order } from "./db";

// 訂單金額上限（含），超過即拒絕
export const MAX_ORDER_TOTAL = 100000;

// 每個檢查回傳錯誤訊息；null 代表通過
type CheckResult = string | null;

export function checkOrderExists(order: Order | null | undefined): CheckResult {
  return order ? null : "訂單不存在";
}

export function checkCustomerId(order: Order): CheckResult {
  return order.customerId && order.customerId.trim() !== "" ? null : "缺少客戶編號";
}

export function checkHasItems(order: Order): CheckResult {
  return order.items && order.items.length > 0 ? null : "訂單沒有商品";
}

// 逐項「先數量、後價格」，保留重構前的錯誤優先順序
export function checkItems(order: Order): CheckResult {
  for (const item of order.items) {
    if (item.qty <= 0) return "數量必須大於 0";
    if (item.price < 0) return "價格不可為負數";
  }
  return null;
}

export function calculateTotal(order: Order): number {
  return order.items.reduce((sum, item) => sum + item.qty * item.price, 0);
}

export function checkTotalWithinLimit(order: Order): CheckResult {
  return calculateTotal(order) <= MAX_ORDER_TOTAL ? null : "訂單金額超過上限";
}

export function validateOrder(order: Order | null | undefined): CheckResult {
  const existsError = checkOrderExists(order);
  if (existsError) return existsError;

  const checks = [checkCustomerId, checkHasItems, checkItems, checkTotalWithinLimit];
  for (const check of checks) {
    const error = check(order as Order);
    if (error) return error;
  }
  return null;
}
