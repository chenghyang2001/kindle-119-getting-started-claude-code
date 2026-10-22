import type { ErrorRequestHandler, RequestHandler } from 'express';
import { ZodError } from 'zod';

/** 應用層錯誤：帶 HTTP 狀態碼與機器可讀的錯誤代碼 */
export class AppError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export const notFound = (resource: string, id: number) =>
  new AppError(404, 'NOT_FOUND', `${resource} ${id} 不存在`);

/** 未匹配任何路由 */
export const routeNotFound: RequestHandler = (req, _res, next) => {
  next(new AppError(404, 'ROUTE_NOT_FOUND', `找不到路由 ${req.method} ${req.path}`));
};

/** 統一錯誤格式：{ error: { code, message, details? } }，500 不洩漏內部細節 */
export const errorHandler: ErrorRequestHandler = (err: unknown, _req, res, _next) => {
  if (err instanceof ZodError) {
    res.status(400).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: '請求資料驗證失敗',
        details: err.issues.map((i) => ({ path: i.path.join('.'), message: i.message })),
      },
    });
    return;
  }
  if (err instanceof AppError) {
    const body: Record<string, unknown> = { code: err.code, message: err.message };
    if (err.details !== undefined) body.details = err.details;
    res.status(err.status).json({ error: body });
    return;
  }
  // express.json() 解析失敗時丟出的 SyntaxError 帶有 status=400
  if (err instanceof SyntaxError && 'status' in err && err.status === 400) {
    res.status(400).json({ error: { code: 'INVALID_JSON', message: 'JSON 格式錯誤' } });
    return;
  }
  console.error('未預期錯誤：', err);
  res.status(500).json({ error: { code: 'INTERNAL_ERROR', message: '伺服器內部錯誤' } });
};
