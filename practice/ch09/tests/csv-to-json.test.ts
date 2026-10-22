import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { convertCsv, parseCsv } from '../src/scripts/csv-to-json.js';

describe('parseCsv', () => {
  it('處理引號、欄位內逗號、"" 跳脫與 CRLF', () => {
    const rows = parseCsv('a,b\r\n"x, y","say ""hi"""\r\n');
    expect(rows).toEqual([
      ['a', 'b'],
      ['x, y', 'say "hi"'],
    ]);
  });

  it('引號未關閉時丟出錯誤', () => {
    expect(() => parseCsv('a\n"oops')).toThrow('引號未關閉');
  });
});

describe('convertCsv', () => {
  it('data/export.csv：9 筆成功、第 8 行價格錯誤被略過', () => {
    const { products, errors } = convertCsv(readFileSync('data/export.csv', 'utf8'));
    expect(products).toHaveLength(9);
    expect(errors).toEqual([{ line: 8, messages: [expect.stringContaining('price')] }]);
    expect(products.find((p) => p.sku === 'COF-330')?.name).toBe('拿鐵 "無糖" 330ml');
    expect(products[0]).toEqual({
      sku: 'PEN-001',
      name: '藍色原子筆',
      category: '文具',
      price: 15,
      quantity: 120,
      updatedAt: '2026-10-01',
    });
  });

  it('缺欄位時丟出錯誤', () => {
    expect(() => convertCsv('sku,name\nA-1,x\n')).toThrow('缺少欄位');
  });

  it('欄位數不符的列被記錄為錯誤', () => {
    const csv = 'sku,name,category,price,quantity,updated_at\nABC-1,x,y,1\n';
    expect(convertCsv(csv).errors[0].messages[0]).toContain('欄位數');
  });
});
