import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchUsers } from '../api/users';
import type { User } from '../types/user';
import { UserList } from './UserList';

vi.mock('../api/users', () => ({ fetchUsers: vi.fn() }));

const mockedFetchUsers = vi.mocked(fetchUsers);

afterEach(() => {
  vi.clearAllMocks();
});

describe('UserList', () => {
  it('載入中顯示提示', () => {
    mockedFetchUsers.mockReturnValue(new Promise<User[]>(() => {}));
    render(<UserList />);
    expect(screen.getByRole('status').textContent).toBe('載入中…');
  });

  it('顯示使用者名稱與 email', async () => {
    mockedFetchUsers.mockResolvedValue([
      { id: 1, name: 'Leanne Graham', email: 'leanne@example.com' },
    ]);
    render(<UserList />);
    expect(await screen.findByText('Leanne Graham')).toBeTruthy();
    expect(screen.getByText('leanne@example.com')).toBeTruthy();
  });

  it('API 失敗時顯示錯誤訊息', async () => {
    mockedFetchUsers.mockRejectedValue(new Error('GET /users 失敗（500）'));
    render(<UserList />);
    const alert = await screen.findByRole('alert');
    expect(alert.textContent).toContain('GET /users 失敗（500）');
  });

  it('空清單時顯示沒有資料', async () => {
    mockedFetchUsers.mockResolvedValue([]);
    render(<UserList />);
    expect(await screen.findByText('目前沒有使用者。')).toBeTruthy();
  });
});
