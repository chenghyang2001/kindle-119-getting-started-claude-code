import { Router } from 'express';
import { categoryCreate, categoryUpdate, idParam } from '../schemas.js';
import type { Store } from '../store.js';

export function categoriesRouter(store: Store): Router {
  const router = Router();
  router.get('/', (_req, res) => {
    res.json({ data: store.listCategories() });
  });
  router.get('/:id', (req, res) => {
    res.json({ data: store.getCategory(idParam.parse(req.params).id) });
  });
  router.post('/', (req, res) => {
    res.status(201).json({ data: store.createCategory(categoryCreate.parse(req.body)) });
  });
  router.patch('/:id', (req, res) => {
    const { id } = idParam.parse(req.params);
    res.json({ data: store.updateCategory(id, categoryUpdate.parse(req.body)) });
  });
  router.delete('/:id', (req, res) => {
    store.deleteCategory(idParam.parse(req.params).id);
    res.status(204).end();
  });
  return router;
}
