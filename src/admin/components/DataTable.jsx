export default function DataTable({ columns, data, keyField = 'id', onRowClick, emptyMessage = 'No data found' }) {
  if (!data?.length) {
    return (
      <div className="rounded-xl dark:bg-untold-surface light:bg-white border dark:border-white/5 light:border-gray-200 p-12 text-center">
        <p className="text-sm dark:text-untold-muted light:text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl dark:bg-untold-surface light:bg-white border dark:border-white/5 light:border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-white/5 light:border-gray-100">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider dark:text-untold-muted light:text-gray-500"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr
                key={row[keyField]}
                onClick={() => onRowClick?.(row)}
                className={`border-b last:border-0 dark:border-white/5 light:border-gray-50
                  ${onRowClick ? 'cursor-pointer hover:dark:bg-white/5 hover:light:bg-gray-50' : ''}
                  transition-colors`}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3.5 dark:text-untold-white light:text-black">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
