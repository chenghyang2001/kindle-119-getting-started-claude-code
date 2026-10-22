import { Router } from 'express';
import { idParam, productCreate, productQuery, productUpdate } from '../schemas.js';
import type { Store } from '../store.js';

export function productsRouter(store: Store): Router {
  const router = Router();
  router.get('/', (req, res) => {
    res.json({ data: store.listProducts(productQuery.parse(req.query)) });
  });
  router.get('/:id', (req, res) => {
    res.json({ data: store.getProduct(idParam.parse(req.params).id) });
  });
  router.get('/:id/movements', (req, res) => {
    const { id } = idParam.parse(req.params);
    store.getProduct(id);
    res.json({ data: store.listMovements(id) });
  });
  router.post('/', (req, res) => {
    res.status(201).json({ data: store.createProduct(productCreate.parse(req.body)) });
  });
  router.patch('/:id', (req, res) => {
    const { id } = idParam.parse(req.params);
    res.json({ data: store.updateProduct(id, productUpdate.parse(req.body)) });
  });
  router.delete('/:id', (req, res) => {
    store.deleteProduct(idParam.parse(req.params).id);
    res.status(204).end();
  });
  return router;
}
