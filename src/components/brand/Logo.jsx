/**
 * UNTOLD brand logos — single wordmark asset across light & dark themes
 */
const V = '?v=6';
const LOGO_FULL = `/brand/untold-logo.png${V}`;
const LOGO_WORDMARK = `/brand/untold-logo-wordmark.png${V}`;

const WORDMARK_SM = 'h-5 w-auto max-w-[72px] sm:h-6 sm:max-w-[84px] shrink-0 object-contain object-left';
const WORDMARK_MD = 'h-6 w-auto max-w-[84px] sm:h-7 sm:max-w-[96px] shrink-0 object-contain object-left';

function LogoImg({ src, alt, className = '' }) {
  return (
    <img
      src={src}
      alt={alt}
      draggable={false}
      decoding="async"
      className={`block max-w-none select-none ${className}`}
    />
  );
}

export default function Logo({ variant = 'full', className = '', showTagline = true }) {
  if (variant === 'nav' || variant === 'compact') {
    return (
      <LogoImg
        src={LOGO_WORDMARK}
        alt="UNTOLD"
        className={`${variant === 'nav' ? WORDMARK_MD : WORDMARK_SM} ${className}`}
      />
    );
  }

  if (variant === 'horizontal') {
    const src = showTagline ? LOGO_FULL : LOGO_WORDMARK;
    return (
      <LogoImg
        src={src}
        alt="UNTOLD — The Story Behind The Glory"
        className={`h-8 sm:h-9 w-auto max-w-[130px] sm:max-w-[150px] object-contain object-left ${className}`}
      />
    );
  }

  if (variant === 'wordmark') {
    return (
      <LogoImg
        src={LOGO_WORDMARK}
        alt="UNTOLD"
        className={`h-7 sm:h-8 w-auto max-w-[110px] object-contain object-left ${className}`}
      />
    );
  }

  return (
    <LogoImg
      src={LOGO_FULL}
      alt="UNTOLD — The Story Behind The Glory"
      className={`w-full max-w-[min(100%,300px)] sm:max-w-[min(100%,340px)] h-auto object-contain object-left ${className}`}
    />
  );
}
