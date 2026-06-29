import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SearchIcon } from '../icons';

export default function MenuSearchField({ onNavigate }) {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onNavigate?.();
      navigate(`/explore?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="menu-search-field">
      <SearchIcon className="w-4 h-4 shrink-0 menu-search-icon" aria-hidden="true" />
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search documentaries, sports…"
        className="menu-search-input"
        aria-label="Search"
      />
    </form>
  );
}
