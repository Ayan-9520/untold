import { SearchIcon } from './AdminIcons';

export default function SearchFilter({ value, onChange, placeholder = 'Search...', filters }) {
  return (
    <div className="flex flex-col sm:flex-row gap-3">
      <div className="relative flex-1">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-untold-muted light:text-gray-400" />
        <input
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-2.5 rounded-lg text-sm outline-none
            dark:bg-untold-surface light:bg-white
            dark:border-white/10 light:border-gray-200 border
            dark:text-untold-white light:text-black
            focus:ring-2 focus:ring-untold-gold/40"
        />
      </div>
      {filters}
    </div>
  );
}
