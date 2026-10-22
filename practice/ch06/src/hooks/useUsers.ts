import { useEffect, useState } from 'react';
import { fetchUsers } from '../api/users';
import type { User } from '../types/user';

export interface UseUsersResult {
  data: User[];
  isLoading: boolean;
  error: Error | null;
}

/** 取得使用者清單；unmount 時以 AbortController 取消進行中的請求 */
export function useUsers(): UseUsersResult {
  const [data, setData] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetchUsers(controller.signal)
      .then((users) => {
        setData(users);
        setError(null);
      })
      .catch((err: unknown) => {
        // 主動取消（unmount）不算錯誤，也不能再更新 state
        if (controller.signal.aborted) return;
        setError(err instanceof Error ? err : new Error(String(err)));
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false);
      });

    return () => controller.abort();
  }, []);

  return { data, isLoading, error };
}
