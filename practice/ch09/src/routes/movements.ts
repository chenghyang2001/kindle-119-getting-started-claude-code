import { Router } from 'express';
import { movementCreate, movementQuery } from '../schemas.js';
import type { Store } from '../store.js';

export function movementsRouter(store: Store): Router {
  const router = Router();
  router.get('/', (req, res) => {
    res.json({ data: store.listMovements(movementQuery.parse(req.query).productId) });
  });
  router.post('/', (req, res) => {
    const { movement, product } = store.createMovement(movementCreate.parse(req.body));
    res.status(201).json({ data: movement, product });
  });
  return router;
}
