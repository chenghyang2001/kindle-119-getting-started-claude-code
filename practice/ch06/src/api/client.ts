/** API 層共用的 fetch 包裝：統一錯誤處理，元件與 hook 不直接呼叫 fetch */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const BASE_URL = 'https://jsonplaceholder.typicode.com';

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, { signal });
  if (!response.ok) {
    throw new ApiError(response.status, `GET ${path} 失敗（${response.status}）`);
  }
  return (await response.json()) as T;
}
