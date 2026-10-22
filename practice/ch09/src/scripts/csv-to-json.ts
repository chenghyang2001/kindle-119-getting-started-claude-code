/**
 * 把 CSV 匯出檔轉成 products.json。
 * 用法：npm run csv:convert -- [輸入 CSV] [輸出 JSON]
 * 預設：data/export.csv → data/products.json
 * 格式錯誤的列不會中斷轉換，會列在 stderr；只要有一列失敗，結束碼為 2。
 */
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { z } from 'zod';

export const csvProductRow = z.object({
  sku: z
    .string()
    .trim()
    .regex(/^[A-Z0-9-]{3,32}$/, 'SKU 格式錯誤'),
  name: z.string().trim().min(1, 'name 不可空白'),
  category: z.string().trim().min(1, 'category 不可空白'),
  price: z.coerce.number({ error: 'price 必須是數字' }).nonnegative('price 不可為負'),
  quantity: z.coerce.number({ error: 'quantity 必須是數字' }).int().nonnegative(),
  updated_at: z.iso.date('updated_at 必須是 YYYY-MM-DD'),
});

export interface ProductJson {
  sku: string;
  name: string;
  category: string;
  price: number;
  quantity: number;
  updatedAt: string;
}

export interface RowError {
  line: number;
  messages: string[];
}

/** 最小 RFC 4180 解析：支援雙引號欄位、欄位內逗號、"" 跳脫與 CRLF */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = '';
  let inQuotes = false;
  const src = text.replace(/^\uFEFF/, ''); // Excel 匯出常帶 BOM

  for (let i = 0; i < src.length; i++) {
    const ch = src[i];
    if (inQuotes) {
      if (ch === '"' && src[i + 1] === '"') {
        field += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      row.push(field);
      field = '';
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && src[i + 1] === '\n') i++;
      row.push(field);
      rows.push(row);
      row = [];
      field = '';
    } else {
      field += ch;
    }
  }
  if (inQuotes) throw new Error('CSV 格式錯誤：引號未關閉');
  if (field !== '' || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((r) => !(r.length === 1 && r[0].trim() === ''));
}

/** 依表頭把每列轉成物件並驗證；回傳成功的商品與失敗列（行號從 1 起算，含表頭） */
export function convertCsv(text: string): { products: ProductJson[]; errors: RowError[] } {
  const [header, ...dataRows] = parseCsv(text);
  if (!header) throw new Error('CSV 是空的');
  const columns = header.map((h) => h.trim());
  const missing = Object.keys(csvProductRow.shape).filter((k) => !columns.includes(k));
  if (missing.length > 0) throw new Error(`CSV 缺少欄位：${missing.join(', ')}`);

  const products: ProductJson[] = [];
  const errors: RowError[] = [];
  dataRows.forEach((cells, idx) => {
    const line = idx + 2;
    if (cells.length !== columns.length) {
      errors.push({ line, messages: [`欄位數 ${cells.length}，預期 ${columns.length}`] });
      return;
    }
    const record = Object.fromEntries(columns.map((c, i) => [c, cells[i]]));
    const parsed = csvProductRow.safeParse(record);
    if (!parsed.success) {
      errors.push({
        line,
        messages: parsed.error.issues.map((i) => `${i.path.join('.')}: ${i.message}`),
      });
      return;
    }
    const { updated_at, ...rest } = parsed.data;
    products.push({ ...rest, updatedAt: updated_at });
  });
  return { products, errors };
}

async function main(): Promise<void> {
  const input = resolve(process.argv[2] ?? 'data/export.csv');
  const output = resolve(process.argv[3] ?? 'data/products.json');

  let text: string;
  try {
    text = await readFile(input, 'utf8');
  } catch (err) {
    throw new Error(`讀不到輸入檔 ${input}：${(err as Error).message}`, { cause: err });
  }

  const { products, errors } = convertCsv(text);
  await writeFile(output, JSON.stringify(products, null, 2) + '\n', 'utf8');

  console.log(`✔ 已轉換 ${products.length} 筆 → ${output}`);
  if (errors.length > 0) {
    console.error(`✘ 略過 ${errors.length} 筆格式錯誤的列：`);
    for (const e of errors) console.error(`  第 ${e.line} 行：${e.messages.join('；')}`);
    process.exitCode = 2;
  }
}

// 只有直接執行時才跑 main，讓測試可以 import 純函式
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((err: unknown) => {
    console.error(`錯誤：${err instanceof Error ? err.message : String(err)}`);
    process.exit(1);
  });
}
