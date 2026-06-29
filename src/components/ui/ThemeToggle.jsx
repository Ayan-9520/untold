import { useTheme } from '../../context/ThemeContext';
import { SunIcon, MoonIcon } from '../icons';

export default function ThemeToggle({ variant = 'icon', className = '' }) {
  const { isDark, toggleTheme, setTheme } = useTheme();

  if (variant === 'segment') {
    return (
      <div className={`theme-segment ${className}`} role="group" aria-label="Theme">
        <button
          type="button"
          onClick={() => setTheme('dark')}
          aria-pressed={isDark}
          className={`theme-segment-btn ${isDark ? 'theme-segment-btn--active' : ''}`}
        >
          <MoonIcon className="w-4 h-4" />
          Dark
        </button>
        <button
          type="button"
          onClick={() => setTheme('light')}
          aria-pressed={!isDark}
          className={`theme-segment-btn ${!isDark ? 'theme-segment-btn--active' : ''}`}
        >
          <SunIcon className="w-4 h-4" />
          Light
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={`site-header-icon-btn ${className}`}
    >
      {isDark ? (
        <SunIcon className="w-5 h-5 text-untold-gold" />
      ) : (
        <MoonIcon className="w-5 h-5 text-gray-800" />
      )}
    </button>
  );
}
