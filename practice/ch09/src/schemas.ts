import { z } from 'zod';

/** 路徑參數 :id → 正整數 */
export const idParam = z.object({ id: z.coerce.number().int().positive() });

export const categoryCreate = z.object({
  name: z.string().trim().min(1).max(100),
  description: z.string().trim().max(500).optional(),
});
export const categoryUpdate = categoryCreate.partial();

export const productCreate = z.object({
  sku: z
    .string()
    .trim()
    .regex(/^[A-Z0-9-]{3,32}$/, 'SKU 只能包含大寫英數與連字號，長度 3–32'),
  name: z.string().trim().min(1).max(200),
  categoryId: z.number().int().positive(),
  price: z.number().nonnegative().multipleOf(0.01),
  quantity: z.number().int().nonnegative().default(0),
});
// 庫存數量只能透過 movements 異動，避免帳實不符
export const productUpdate = productCreate.omit({ quantity: true }).partial();

export const productQuery = z.object({
  categoryId: z.coerce.number().int().positive().optional(),
  q: z.string().trim().min(1).optional(),
});

export const movementCreate = z.object({
  productId: z.number().int().positive(),
  type: z.enum(['in', 'out', 'adjust']),
  // in/out 為正數；adjust 可正可負但不可為 0
  quantity: z
    .number()
    .int()
    .refine((n) => n !== 0, '數量不可為 0'),
  note: z.string().trim().max(500).optional(),
});

export const movementQuery = z.object({
  productId: z.coerce.number().int().positive().optional(),
});

export type CategoryInput = z.infer<typeof categoryCreate>;
export type ProductInput = z.infer<typeof productCreate>;
export type MovementInput = z.infer<typeof movementCreate>;
