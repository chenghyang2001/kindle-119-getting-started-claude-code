import { Db, DbWriter, Order } from "../src/db";

export type FakeDb = Db & {
  orders: Order[];
  stockCalls: Array<[string, number]>;
  // 設定後，對該商品扣庫存會丟錯（模擬寫入失敗）
  failOnStockItemId?: string;
};

// 記憶體假 db：交易開始先快照，失敗時還原快照
export function createFakeDb(): FakeDb {
  const db: FakeDb = {
    orders: [],
    stockCalls: [],
    async insertOrder(order) {
      db.orders.push(order);
      return `ORD-${db.orders.length}`;
    },
    async decrementStock(itemId, qty) {
      if (itemId === db.failOnStockItemId) {
        throw new Error(`扣庫存失敗：${itemId}`);
      }
      db.stockCalls.push([itemId, qty]);
    },
    async transaction<T>(fn: (tx: DbWriter) => Promise<T>): Promise<T> {
      const ordersSnapshot = [...db.orders];
      const stockSnapshot = [...db.stockCalls];
      try {
        return await fn(db);
      } catch (error) {
        db.orders = ordersSnapshot;
        db.stockCalls = stockSnapshot;
        throw error;
      }
    },
  };
  return db;
}
