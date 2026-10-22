import { Db, Order } from "./db";
import { validateOrder } from "./validation";

export interface ProcessResult {
  ok: boolean;
  orderId?: string;
  error?: string;
}

export const WRITE_FAILED_ERROR = "寫入失敗，已回滾";

export async function processOrder(order: Order, db: Db): Promise<ProcessResult> {
  const validationError = validateOrder(order);
  if (validationError) return { ok: false, error: validationError };

  try {
    const orderId = await db.transaction(async (tx) => {
      const newOrderId = await tx.insertOrder(order);
      for (const item of order.items) {
        await tx.decrementStock(item.id, item.qty);
      }
      return newOrderId;
    });
    return { ok: true, orderId };
  } catch (error) {
    // 交易已回滾；只回傳通用訊息，不把內部錯誤細節外洩給呼叫端
    console.error("processOrder 寫入失敗：", error);
    return { ok: false, error: WRITE_FAILED_ERROR };
  }
}
