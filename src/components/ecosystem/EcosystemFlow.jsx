import { Link } from 'react-router-dom';
import { PRODUCTS, ECOSYSTEM_FLOW } from '../../config/ecosystem';

const PRODUCT_STYLES = {
  ORIGINALS: 'border-untold-gold/40 bg-untold-gold/10 text-untold-gold',
  STUDIO: 'border-blue-400/40 bg-blue-500/10 text-blue-300',
  AI: 'border-purple-400/40 bg-purple-500/10 text-purple-300',
};

/**
 * Step-by-step content lifecycle across products.
 * @param {{ compact?: boolean, showLinks?: boolean, showPhaseBadges?: boolean, phaseFilter?: 1 | 2 | null }} props
 */
export default function EcosystemFlow({
  compact = false,
  showLinks = false,
  showPhaseBadges = false,
  phaseFilter = null,
}) {
  const steps = phaseFilter
    ? ECOSYSTEM_FLOW.filter((s) => s.phase === phaseFilter)
    : ECOSYSTEM_FLOW;

  return (
    <div className={`ecosystem-flow ${compact ? 'ecosystem-flow--compact' : ''}`}>
      <div className="ecosystem-flow-products">
        {['ORIGINALS', 'STUDIO', 'AI'].map((key) => {
          const p = PRODUCTS[key];
          const href = p.basePath === '/' ? '/' : p.basePath;
          const inner = (
            <div className={`ecosystem-flow-product ${PRODUCT_STYLES[key]}`}>
              <p className="text-[10px] uppercase tracking-widest opacity-80">
                Phase {p.phase} · {p.shortName}
              </p>
              <p className="font-semibold text-sm mt-0.5">{p.name.replace('UNTOLD ', '')}</p>
              {!compact && (
                <p className="text-[11px] mt-1 opacity-70 leading-snug">{p.description}</p>
              )}
            </div>
          );
          return showLinks ? (
            <Link key={key} to={href} className="ecosystem-flow-product-link">
              {inner}
            </Link>
          ) : (
            <div key={key}>{inner}</div>
          );
        })}
      </div>

      {!compact && (
        <ol className="ecosystem-flow-steps">
          {steps.map((item, i) => (
            <li
              key={item.step}
              className={`ecosystem-flow-step ${item.phase === 2 ? 'ecosystem-flow-step--phase-2' : ''}`}
            >
              <span className="ecosystem-flow-step-num">{i + 1}</span>
              <span className="ecosystem-flow-step-text">{item.step}</span>
              {showPhaseBadges && (
                <span className="ecosystem-flow-step-phase">P{item.phase}</span>
              )}
              <span className={`ecosystem-flow-step-badge ${PRODUCT_STYLES[item.product]}`}>
                {PRODUCTS[item.product].shortName}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
