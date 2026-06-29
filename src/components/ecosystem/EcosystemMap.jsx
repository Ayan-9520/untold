import { Link } from 'react-router-dom';
import { PRODUCTS, ECOSYSTEM_CONNECTIONS } from '../../config/ecosystem';

const PRODUCT_STYLES = {
  ORIGINALS: 'ecosystem-map-node--originals',
  STUDIO: 'ecosystem-map-node--studio',
  AI: 'ecosystem-map-node--ai',
};

const NODE_ORDER = ['STUDIO', 'ORIGINALS', 'AI'];

/**
 * Three-product map with labeled connections.
 * @param {{ showLinks?: boolean, highlightPhase?: 1 | 2 | null }} props
 */
export default function EcosystemMap({ showLinks = false, highlightPhase = null }) {
  const connections = highlightPhase
    ? ECOSYSTEM_CONNECTIONS.filter((c) => c.phase === highlightPhase)
    : ECOSYSTEM_CONNECTIONS;

  return (
    <div className="ecosystem-map">
      <div className="ecosystem-map-nodes">
        {NODE_ORDER.map((key) => {
          const p = PRODUCTS[key];
          const href = p.basePath === '/' ? '/' : p.basePath;
          const dimmed = highlightPhase && p.phase !== highlightPhase && key !== 'STUDIO';
          const inner = (
            <div className={`ecosystem-map-node ${PRODUCT_STYLES[key]} ${dimmed ? 'is-dimmed' : ''}`}>
              <span className="ecosystem-map-node-phase">Phase {p.phase}</span>
              <p className="ecosystem-map-node-name">{p.shortName}</p>
              <p className="ecosystem-map-node-full">{p.name}</p>
              <p className="ecosystem-map-node-role">{p.role}</p>
            </div>
          );
          const linkable = showLinks && (key === 'ORIGINALS' || key === 'STUDIO' || key === 'AI');
          return linkable ? (
            <Link key={key} to={href} className="ecosystem-map-node-link">
              {inner}
            </Link>
          ) : (
            <div key={key}>{inner}</div>
          );
        })}
      </div>

      <ul className="ecosystem-map-connections">
        {connections.map((c) => (
          <li
            key={`${c.from}-${c.to}-${c.label}`}
            className={`ecosystem-map-connection ecosystem-map-connection--phase-${c.phase} ${c.internal ? 'is-internal' : ''}`}
          >
            <span className="ecosystem-map-connection-from">{PRODUCTS[c.from].shortName}</span>
            <span className="ecosystem-map-connection-arrow" aria-hidden>→</span>
            <span className="ecosystem-map-connection-to">{PRODUCTS[c.to].shortName}</span>
            <span className="ecosystem-map-connection-label">{c.label}</span>
            <span className="ecosystem-map-connection-phase">P{c.phase}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
