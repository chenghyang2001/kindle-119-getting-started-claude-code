// 假資料庫介面：兩個寫入動作＋交易
export interface OrderItem {
  id: string;
  qty: number;
  price: number;
}

export interface Order {
  customerId: string;
  items: OrderItem[];
}

export interface DbWriter {
  insertOrder(order: Order): Promise<string>;
  decrementStock(itemId: string, qty: number): Promise<void>;
}

export interface Db extends DbWriter {
  // fn 內丟錯 → 回滾所有寫入並把錯誤往上丟
  transaction<T>(fn: (tx: DbWriter) => Promise<T>): Promise<T>;
}
