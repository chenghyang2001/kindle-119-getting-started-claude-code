import { renderHook, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchUsers } from '../api/users';
import type { User } from '../types/user';
import { useUsers } from './useUsers';

vi.mock('../api/users', () => ({ fetchUsers: vi.fn() }));

const mockedFetchUsers = vi.mocked(fetchUsers);

const sampleUsers: User[] = [
  { id: 1, name: 'Leanne Graham', email: 'leanne@example.com' },
  { id: 2, name: 'Ervin Howell', email: 'ervin@example.com' },
];

afterEach(() => {
  vi.clearAllMocks();
});

describe('useUsers', () => {
  it('成功時回傳使用者清單', async () => {
    mockedFetchUsers.mockResolvedValue(sampleUsers);

    const { result } = renderHook(() => useUsers());
    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toEqual(sampleUsers);
    expect(result.current.error).toBeNull();
  });

  it('API 失敗時回傳 error', async () => {
    mockedFetchUsers.mockRejectedValue(new Error('GET /users 失敗（500）'));

    const { result } = renderHook(() => useUsers());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error?.message).toBe('GET /users 失敗（500）');
    expect(result.current.data).toEqual([]);
  });

  it('unmount 時取消請求', () => {
    mockedFetchUsers.mockReturnValue(new Promise<User[]>(() => {}));

    const { unmount } = renderHook(() => useUsers());
    const signal = mockedFetchUsers.mock.calls[0][0];
    expect(signal?.aborted).toBe(false);

    unmount();
    expect(signal?.aborted).toBe(true);
  });
});
