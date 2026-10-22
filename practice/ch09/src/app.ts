import express, { type Express } from 'express';
import { errorHandler, routeNotFound } from './errors.js';
import { categoriesRouter } from './routes/categories.js';
import { movementsRouter } from './routes/movements.js';
import { productsRouter } from './routes/products.js';
import { Store } from './store.js';

/** 建立 app；可注入 Store，讓每個測試拿到乾淨的資料 */
export function createApp(store: Store = new Store()): Express {
  const app = express();
  app.use(express.json({ limit: '100kb' }));

  app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
  });
  app.use('/api/categories', categoriesRouter(store));
  app.use('/api/products', productsRouter(store));
  app.use('/api/movements', movementsRouter(store));

  app.use(routeNotFound);
  app.use(errorHandler);
  return app;
}
