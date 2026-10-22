import type { User } from '../types/user';
import { apiGet } from './client';

export function fetchUsers(signal?: AbortSignal): Promise<User[]> {
  return apiGet<User[]>('/users', signal);
}
