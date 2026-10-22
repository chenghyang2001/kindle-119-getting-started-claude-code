import { processOrder } from "../src/processOrder";
import { createFakeDb } from "./fakeDb";

const validOrder = () => ({
  customerId: "C001",
  items: [
    { id: "A", qty: 2, price: 100 },
    { id: "B", qty: 1, price: 50 },
  ],
});

describe("processOrder", () => {
  test("合法訂單：寫入訂單並扣庫存", async () => {
    const db = createFakeDb();
    const result = await processOrder(validOrder(), db);
    expect(result).toEqual({ ok: true, orderId: "ORD-1" });
    expect(db.orders).toHaveLength(1);
    expect(db.stockCalls).toEqual([["A", 2], ["B", 1]]);
  });

  test.each([
    ["訂單不存在", null],
    ["缺少客戶編號", { customerId: "  ", items: [{ id: "A", qty: 1, price: 1 }] }],
    ["訂單沒有商品", { customerId: "C001", items: [] }],
    ["數量必須大於 0", { customerId: "C001", items: [{ id: "A", qty: 0, price: 1 }] }],
    ["價格不可為負數", { customerId: "C001", items: [{ id: "A", qty: 1, price: -1 }] }],
    ["訂單金額超過上限", { customerId: "C001", items: [{ id: "A", qty: 2, price: 60000 }] }],
  ])("驗證失敗：%s，且不寫入 db", async (error, order) => {
    const db = createFakeDb();
    const result = await processOrder(order as any, db);
    expect(result).toEqual({ ok: false, error });
    expect(db.orders).toHaveLength(0);
    expect(db.stockCalls).toHaveLength(0);
  });
});

describe("processOrder 交易", () => {
  test("扣第二個商品庫存失敗：回傳錯誤，且訂單與庫存都回滾", async () => {
    const db = createFakeDb();
    db.failOnStockItemId = "B";
    const errorSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    const result = await processOrder(validOrder(), db);

    expect(result).toEqual({ ok: false, error: "寫入失敗，已回滾" });
    expect(db.orders).toHaveLength(0);
    expect(db.stockCalls).toHaveLength(0);
    expect(errorSpy).toHaveBeenCalled();
    errorSpy.mockRestore();
  });

  test("回滾後同一個 db 仍可成功寫入下一張訂單", async () => {
    const db = createFakeDb();
    db.failOnStockItemId = "B";
    jest.spyOn(console, "error").mockImplementation(() => {});
    await processOrder(validOrder(), db);
    db.failOnStockItemId = undefined;

    const result = await processOrder(validOrder(), db);

    expect(result).toEqual({ ok: true, orderId: "ORD-1" });
    expect(db.stockCalls).toEqual([["A", 2], ["B", 1]]);
  });
});

// 避免 console.error 的 spy 漏到其他測試
afterEach(() => jest.restoreAllMocks());
