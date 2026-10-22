import { useUsers } from '../hooks/useUsers';
import styles from './UserList.module.css';

export function UserList() {
  const { data: users, isLoading, error } = useUsers();

  if (isLoading) return <p role="status">載入中…</p>;
  if (error) return <p role="alert" className={styles.error}>載入失敗：{error.message}</p>;
  if (users.length === 0) return <p>目前沒有使用者。</p>;

  return (
    <ul className={styles.list} aria-label="使用者清單">
      {users.map((user) => (
        <li key={user.id} className={styles.item}>
          <span className={styles.name}>{user.name}</span>
          <span className={styles.email}>{user.email}</span>
        </li>
      ))}
    </ul>
  );
}
