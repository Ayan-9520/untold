/** Split "UNTOLD: THE KING ERA — KOHLI" into headline + subject */
export function parseHeroTitle(featuredTitle = '') {
  const stripped = featuredTitle.replace(/^UNTOLD:\s*/i, '').trim();
  const dashIdx = stripped.indexOf(' — ');

  if (dashIdx >= 0) {
    return {
      headline: stripped.slice(0, dashIdx).trim(),
      subject: stripped.slice(dashIdx + 3).trim(),
    };
  }

  return { headline: stripped || featuredTitle, subject: '' };
}

export default function HeroTitle({ featuredTitle }) {
  const { headline, subject } = parseHeroTitle(featuredTitle);

  return (
    <div className="hero-title-block">
      <h1 className="hero-title-headline">{headline}</h1>
      {subject ? (
        <>
          <span className="hero-title-rule" aria-hidden="true" />
          <span className="hero-title-subject">{subject}</span>
        </>
      ) : null}
    </div>
  );
}
