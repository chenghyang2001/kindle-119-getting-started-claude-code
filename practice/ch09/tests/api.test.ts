import request from 'supertest';
import { beforeEach, describe, expect, it } from 'vitest';
import type { Express } from 'express';
import { createApp } from '../src/app.js';

let app: Express;

/** 建立一個分類與一個商品，回傳兩者 id */
async function seed(quantity = 10) {
  const cat = await request(app).post('/api/categories').send({ name: '文具' }).expect(201);
  const prod = await request(app)
    .post('/api/products')
    .send({ sku: 'PEN-001', name: '藍色原子筆', categoryId: cat.body.data.id, price: 15, quantity })
    .expect(201);
  return { categoryId: cat.body.data.id as number, productId: prod.body.data.id as number };
}

beforeEach(() => {
  app = createApp(); // 每個測試一份乾淨的記憶體資料
});

describe('基本', () => {
  it('GET /health 回傳 ok', async () => {
    const res = await request(app).get('/health').expect(200);
    expect(res.body).toEqual({ status: 'ok' });
  });

  it('未知路由回傳一致的 404 格式', async () => {
    const res = await request(app).get('/api/nope').expect(404);
    expect(res.body.error.code).toBe('ROUTE_NOT_FOUND');
  });

  it('壞掉的 JSON 回傳 400 INVALID_JSON', async () => {
    const res = await request(app)
      .post('/api/categories')
      .set('Content-Type', 'application/json')
      .send('{"name":')
      .expect(400);
    expect(res.body.error.code).toBe('INVALID_JSON');
  });
});

describe('categories', () => {
  it('可建立、查詢、更新、刪除', async () => {
    const created = await request(app)
      .post('/api/categories')
      .send({ name: '飲料', description: '瓶裝' })
      .expect(201);
    const id = created.body.data.id as number;

    const list = await request(app).get('/api/categories').expect(200);
    expect(list.body.data).toHaveLength(1);

    const patched = await request(app)
      .patch(`/api/categories/${id}`)
      .send({ name: '飲品' })
      .expect(200);
    expect(patched.body.data.name).toBe('飲品');

    await request(app).delete(`/api/categories/${id}`).expect(204);
    await request(app).get(`/api/categories/${id}`).expect(404);
  });

  it('名稱空白時回傳 400 並附欄位明細', async () => {
    const res = await request(app).post('/api/categories').send({ name: '   ' }).expect(400);
    expect(res.body.error.code).toBe('VALIDATION_ERROR');
    expect(res.body.error.details[0].path).toBe('name');
  });

  it('重複名稱回傳 409', async () => {
    await request(app).post('/api/categories').send({ name: '文具' }).expect(201);
    const res = await request(app).post('/api/categories').send({ name: '文具' }).expect(409);
    expect(res.body.error.code).toBe('DUPLICATE_CATEGORY');
  });

  it('仍有商品的分類不可刪除', async () => {
    const { categoryId } = await seed();
    const res = await request(app).delete(`/api/categories/${categoryId}`).expect(409);
    expect(res.body.error.code).toBe('CATEGORY_IN_USE');
  });

  it('非數字 id 回傳 400', async () => {
    await request(app).get('/api/categories/abc').expect(400);
  });
});

describe('products', () => {
  it('建立後可依分類與關鍵字篩選', async () => {
    const { categoryId } = await seed();
    const byCat = await request(app).get(`/api/products?categoryId=${categoryId}`).expect(200);
    expect(byCat.body.data).toHaveLength(1);
    const byQ = await request(app).get('/api/products?q=pen').expect(200);
    expect(byQ.body.data[0].sku).toBe('PEN-001');
    const none = await request(app).get('/api/products?q=zzz').expect(200);
    expect(none.body.data).toHaveLength(0);
  });

  it('分類不存在時回傳 404', async () => {
    const res = await request(app)
      .post('/api/products')
      .send({ sku: 'X-001', name: 'x', categoryId: 999, price: 1 })
      .expect(404);
    expect(res.body.error.message).toContain('Category 999');
  });

  it('SKU 格式錯誤、價格為負時回傳 400', async () => {
    const { categoryId } = await seed();
    const res = await request(app)
      .post('/api/products')
      .send({ sku: 'bad sku', name: 'x', categoryId, price: -1 })
      .expect(400);
    const paths = (res.body.error.details as { path: string }[]).map((d) => d.path);
    expect(paths).toEqual(expect.arrayContaining(['sku', 'price']));
  });

  it('重複 SKU 回傳 409', async () => {
    const { categoryId } = await seed();
    await request(app)
      .post('/api/products')
      .send({ sku: 'PEN-001', name: '重複', categoryId, price: 1 })
      .expect(409);
  });

  it('PATCH 可改價格，但會忽略 quantity', async () => {
    const { productId } = await seed(10);
    const res = await request(app)
      .patch(`/api/products/${productId}`)
      .send({ price: 20, quantity: 999 })
      .expect(200);
    expect(res.body.data.price).toBe(20);
    expect(res.body.data.quantity).toBe(10);
  });
});

describe('movements', () => {
  it('進貨、出貨、盤點調整會正確更新庫存', async () => {
    const { productId } = await seed(10);
    await request(app)
      .post('/api/movements')
      .send({ productId, type: 'in', quantity: 5 })
      .expect(201);
    await request(app)
      .post('/api/movements')
      .send({ productId, type: 'out', quantity: 3 })
      .expect(201);
    const adj = await request(app)
      .post('/api/movements')
      .send({ productId, type: 'adjust', quantity: -2, note: '盤點短少' })
      .expect(201);
    expect(adj.body.product.quantity).toBe(10);

    const history = await request(app).get(`/api/products/${productId}/movements`).expect(200);
    expect(history.body.data.map((m: { type: string }) => m.type)).toEqual(['in', 'out', 'adjust']);
  });

  it('出貨超過庫存回傳 409 INSUFFICIENT_STOCK，庫存不變', async () => {
    const { productId } = await seed(2);
    const res = await request(app)
      .post('/api/movements')
      .send({ productId, type: 'out', quantity: 5 })
      .expect(409);
    expect(res.body.error).toMatchObject({
      code: 'INSUFFICIENT_STOCK',
      details: { available: 2, requested: 5 },
    });
    const prod = await request(app).get(`/api/products/${productId}`).expect(200);
    expect(prod.body.data.quantity).toBe(2);
  });

  it('數量為 0、in 為負數、type 不合法都回傳 400', async () => {
    const { productId } = await seed();
    await request(app)
      .post('/api/movements')
      .send({ productId, type: 'in', quantity: 0 })
      .expect(400);
    const neg = await request(app)
      .post('/api/movements')
      .send({ productId, type: 'in', quantity: -1 })
      .expect(400);
    expect(neg.body.error.code).toBe('INVALID_QUANTITY');
    await request(app)
      .post('/api/movements')
      .send({ productId, type: 'gift', quantity: 1 })
      .expect(400);
  });

  it('有異動紀錄的商品不可刪除', async () => {
    const { productId } = await seed();
    await request(app)
      .post('/api/movements')
      .send({ productId, type: 'in', quantity: 1 })
      .expect(201);
    const res = await request(app).delete(`/api/products/${productId}`).expect(409);
    expect(res.body.error.code).toBe('PRODUCT_HAS_MOVEMENTS');
  });
});
