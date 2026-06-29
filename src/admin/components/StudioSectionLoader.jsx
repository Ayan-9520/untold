/** Loading skeleton for Studio list sections. */
export default function StudioSectionLoader({ rows = 3 }) {
  return (
    <div className="studio-section-loader" aria-busy="true">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="studio-section-loader-row" />
      ))}
    </div>
  );
}
