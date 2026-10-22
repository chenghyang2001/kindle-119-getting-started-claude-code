import { AppError, notFound } from './errors.js';
import type { CategoryInput, MovementInput, ProductInput } from './schemas.js';

export interface Category {
  id: number;
  name: string;
  description?: string;
}
export interface Product {
  id: number;
  sku: string;
  name: string;
  categoryId: number;
  price: number;
  quantity: number;
  createdAt: string;
  updatedAt: string;
}
export interface Movement {
  id: number;
  productId: number;
  type: 'in' | 'out' | 'adjust';
  quantity: number;
  note?: string;
  createdAt: string;
}

/** 記憶體資料庫：對應 products / categories / movements 三張表，每個 app 實例一份 */
export class Store {
  private categories = new Map<number, Category>();
  private products = new Map<number, Product>();
  private movements: Movement[] = [];
  private seq = { category: 0, product: 0, movement: 0 };

  // ---- categories ----
  listCategories(): Category[] {
    return [...this.categories.values()];
  }
  getCategory(id: number): Category {
    const found = this.categories.get(id);
    if (!found) throw notFound('Category', id);
    return found;
  }
  createCategory(input: CategoryInput): Category {
    this.assertUniqueCategoryName(input.name);
    const category = { id: ++this.seq.category, ...input };
    this.categories.set(category.id, category);
    return category;
  }
  updateCategory(id: number, input: Partial<CategoryInput>): Category {
    const current = this.getCategory(id);
    if (input.name !== undefined && input.name !== current.name) {
      this.assertUniqueCategoryName(input.name);
    }
    const updated = { ...current, ...input };
    this.categories.set(id, updated);
    return updated;
  }
  deleteCategory(id: number): void {
    this.getCategory(id);
    if ([...this.products.values()].some((p) => p.categoryId === id)) {
      throw new AppError(409, 'CATEGORY_IN_USE', `Category ${id} 仍有商品，無法刪除`);
    }
    this.categories.delete(id);
  }

  // ---- products ----
  listProducts(filter: { categoryId?: number; q?: string } = {}): Product[] {
    const keyword = filter.q?.toLowerCase();
    return [...this.products.values()].filter((p) => {
      if (filter.categoryId !== undefined && p.categoryId !== filter.categoryId) return false;
      if (keyword === undefined) return true;
      return p.name.toLowerCase().includes(keyword) || p.sku.toLowerCase().includes(keyword);
    });
  }
  getProduct(id: number): Product {
    const found = this.products.get(id);
    if (!found) throw notFound('Product', id);
    return found;
  }
  createProduct(input: ProductInput): Product {
    this.getCategory(input.categoryId);
    this.assertUniqueSku(input.sku);
    const now = new Date().toISOString();
    const product = { id: ++this.seq.product, ...input, createdAt: now, updatedAt: now };
    this.products.set(product.id, product);
    return product;
  }
  updateProduct(id: number, input: Partial<Omit<ProductInput, 'quantity'>>): Product {
    const current = this.getProduct(id);
    if (input.categoryId !== undefined) this.getCategory(input.categoryId);
    if (input.sku !== undefined && input.sku !== current.sku) this.assertUniqueSku(input.sku);
    const updated = { ...current, ...input, updatedAt: new Date().toISOString() };
    this.products.set(id, updated);
    return updated;
  }
  deleteProduct(id: number): void {
    this.getProduct(id);
    if (this.movements.some((m) => m.productId === id)) {
      throw new AppError(409, 'PRODUCT_HAS_MOVEMENTS', `Product ${id} 已有庫存異動紀錄，無法刪除`);
    }
    this.products.delete(id);
  }

  // ---- movements ----
  listMovements(productId?: number): Movement[] {
    return this.movements.filter((m) => productId === undefined || m.productId === productId);
  }
  createMovement(input: MovementInput): { movement: Movement; product: Product } {
    const product = this.getProduct(input.productId);
    if (input.type !== 'adjust' && input.quantity < 0) {
      throw new AppError(400, 'INVALID_QUANTITY', 'in/out 的數量必須為正數');
    }
    const delta = input.type === 'out' ? -input.quantity : input.quantity;
    if (product.quantity + delta < 0) {
      throw new AppError(409, 'INSUFFICIENT_STOCK', `庫存不足：目前 ${product.quantity}`, {
        available: product.quantity,
        requested: Math.abs(delta),
      });
    }
    const now = new Date().toISOString();
    const movement: Movement = { id: ++this.seq.movement, ...input, createdAt: now };
    this.movements.push(movement);
    const updated = { ...product, quantity: product.quantity + delta, updatedAt: now };
    this.products.set(product.id, updated);
    return { movement, product: updated };
  }

  private assertUniqueCategoryName(name: string): void {
    if ([...this.categories.values()].some((c) => c.name === name)) {
      throw new AppError(409, 'DUPLICATE_CATEGORY', `分類名稱「${name}」已存在`);
    }
  }
  private assertUniqueSku(sku: string): void {
    if ([...this.products.values()].some((p) => p.sku === sku)) {
      throw new AppError(409, 'DUPLICATE_SKU', `SKU ${sku} 已存在`);
    }
  }
}
