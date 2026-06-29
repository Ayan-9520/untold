export default function Chip({
  children,
  active = false,
  onClick,
  className = '',
}) {
  const Tag = onClick ? 'button' : 'span';

  return (
    <Tag
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      className={`inline-flex items-center shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-all duration-200
        ${active
          ? 'bg-untold-gold text-untold-dark shadow-md shadow-untold-gold/20'
          : 'dark:bg-untold-surface light:bg-gray-100 dark:text-untold-muted light:text-gray-600 dark:border-untold-border light:border-gray-200 border hover:border-untold-gold/50 hover:text-untold-gold'
        }
        ${onClick ? 'cursor-pointer' : ''}
        ${className}`}
    >
      {children}
    </Tag>
  );
}
