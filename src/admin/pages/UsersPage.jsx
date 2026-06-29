import { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import SearchFilter from '../components/SearchFilter';
import AdminErrorBanner from '../components/AdminErrorBanner';
import { users as usersApi } from '../api/adminApi';
import { DownloadIcon } from '../components/AdminIcons';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchUsers = () => {
    setLoading(true);
    setError(null);
    usersApi.list({ page, page_size: 20 })
      .then((data) => {
        setUsers(data.items);
        setTotal(data.total);
      })
      .catch((err) => setError(err.message || 'Failed to load users'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchUsers(); }, [page]);

  const filtered = users.filter(
    (u) =>
      u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
  );

  const handleDeactivate = async (user) => {
    if (!confirm(`Deactivate ${user.full_name}?`)) return;
    await usersApi.deactivate(user.id);
    fetchUsers();
  };

  const exportReport = () => {
    const csv = ['Name,Email,Role,Status,Created']
      .concat(filtered.map((u) =>
        `"${u.full_name}","${u.email}","${u.role}","${u.is_active ? 'Active' : 'Inactive'}","${u.created_at}"`
      )).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'untold-users-report.csv';
    a.click();
  };

  const columns = [
    {
      key: 'name',
      label: 'User',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-untold-gold/20 flex items-center justify-center text-xs font-bold text-untold-gold">
            {row.full_name?.[0]?.toUpperCase()}
          </div>
          <div>
            <p className="font-medium">{row.full_name}</p>
            <p className="text-xs dark:text-untold-muted light:text-gray-500">{row.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'role',
      label: 'Role',
      render: (row) => (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium
          ${row.is_admin ? 'bg-untold-gold/15 text-untold-gold' : 'dark:bg-white/5 light:bg-gray-100 dark:text-untold-muted light:text-gray-600'}`}>
          {row.is_admin ? 'Admin' : row.role}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => (
        <span className={`inline-flex items-center gap-1.5 text-xs ${row.is_active ? 'text-emerald-400' : 'text-red-400'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${row.is_active ? 'bg-emerald-400' : 'bg-red-400'}`} />
          {row.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Joined',
      render: (row) => new Date(row.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: '',
      render: (row) =>
        row.is_active && !row.is_admin ? (
          <button
            onClick={(e) => { e.stopPropagation(); handleDeactivate(row); }}
            className="text-xs text-red-400 hover:underline"
          >
            Deactivate
          </button>
        ) : null,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">User Management</h1>
          <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">{total} total users</p>
        </div>
        <button
          onClick={exportReport}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
            dark:bg-white/5 light:bg-white border dark:border-white/10 light:border-gray-200
            hover:bg-untold-gold/10 hover:text-untold-gold transition-colors"
        >
          <DownloadIcon className="w-4 h-4" />
          Export Report
        </button>
      </div>

      {error && <AdminErrorBanner message={error} onRetry={fetchUsers} />}

      <SearchFilter value={search} onChange={setSearch} placeholder="Search users..." />

      {loading ? (
        <div className="h-64 rounded-xl skeleton" />
      ) : (
        <DataTable columns={columns} data={filtered} emptyMessage="No users found" />
      )}

      {total > 20 && (
        <div className="flex justify-center gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1.5 rounded-lg text-sm dark:bg-white/5 disabled:opacity-40"
          >
            Previous
          </button>
          <span className="px-3 py-1.5 text-sm dark:text-untold-muted">Page {page}</span>
          <button
            disabled={page * 20 >= total}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1.5 rounded-lg text-sm dark:bg-white/5 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
