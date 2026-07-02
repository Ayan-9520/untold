import { useState } from 'react';
import { users as usersApi } from '../../../api/adminApi';
import { STUDIO_ROLES } from '../constants';
import { useEffect } from 'react';

export default function ProjectTeamPanel({ project, onAssign, onRemove, loading }) {
  const [userId, setUserId] = useState('');
  const [role, setRole] = useState('viewer');
  const [userList, setUserList] = useState([]);

  useEffect(() => {
    usersApi.list({ page: 1, page_size: 50 }).then((d) => setUserList(d.items || [])).catch(() => {});
  }, []);

  const handleAssign = (e) => {
    e.preventDefault();
    if (!userId) return;
    onAssign({ user_id: Number(userId), role });
    setUserId('');
  };

  return (
    <div className="space-y-4">
      <ul className="space-y-2">
        {(project.members || []).map((m) => (
          <li key={m.user_id} className="flex items-center justify-between gap-3 rounded-lg border dark:border-white/10 px-3 py-2">
            <div className="min-w-0">
              <p className="text-sm dark:text-white light:text-black">{m.full_name}</p>
              <p className="text-xs dark:text-untold-muted">{m.email}</p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-[10px] uppercase tracking-wider text-untold-gold capitalize">{m.role}</span>
              <button type="button" onClick={() => onRemove(m.user_id)} className="text-xs text-red-400 hover:underline">
                Remove
              </button>
            </div>
          </li>
        ))}
      </ul>
      <form onSubmit={handleAssign} className="flex flex-wrap gap-2 items-end border-t dark:border-white/10 pt-4">
        <label className="flex-1 min-w-[140px]">
          <span className="text-xs dark:text-untold-muted">User</span>
          <select
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="mt-1 w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            <option value="">Select user…</option>
            {userList.map((u) => (
              <option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>
            ))}
          </select>
        </label>
        <label>
          <span className="text-xs dark:text-untold-muted">Role</span>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="mt-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            {STUDIO_ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </label>
        <button type="submit" disabled={loading || !userId} className="px-3 py-1.5 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50">
          Assign
        </button>
      </form>
    </div>
  );
}
