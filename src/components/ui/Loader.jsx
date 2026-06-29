import { Link } from 'react-router-dom';
import Logo from '../../components/brand/Logo';

export default function Loader({ label = 'Loading', fullScreen = false }) {
  return (
    <div
      className={`ott-loader flex flex-col items-center justify-center gap-6
        ${fullScreen ? 'min-h-screen bg-untold-dark' : 'py-16'}`}
      role="status"
      aria-live="polite"
      aria-label={label}
    >
      <div className="ott-loader-logo">
        <Logo variant="compact" />
      </div>
      <div className="ott-loader-bar" aria-hidden="true">
        <div className="ott-loader-bar-fill" />
      </div>
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-untold-gold">{label}</p>
      <p className="text-[10px] text-untold-muted tracking-widest uppercase">The Story Behind The Glory</p>
    </div>
  );
}
