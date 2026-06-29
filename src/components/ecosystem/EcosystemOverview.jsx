import { Link } from 'react-router-dom';
import {
  PRODUCTS,
  STUDIO_PIPELINE,
  REVENUE_FLYWHEEL,
  AI_MODULES,
  AI_SAAS_PLANS,
  studioPath,
  aiPath,
} from '../../config/ecosystem';
import EcosystemPhases from './EcosystemPhases';
import EcosystemMap from './EcosystemMap';
import EcosystemFlow from './EcosystemFlow';

const PRODUCT_STYLES = {
  ORIGINALS: 'border-untold-gold/40 bg-untold-gold/10 text-untold-gold',
  STUDIO: 'border-blue-400/40 bg-blue-500/10 text-blue-300',
  AI: 'border-purple-400/40 bg-purple-500/10 text-purple-300',
};

/**
 * Full ecosystem — phases, map, flow, pipeline, flywheel.
 * @param {{
 *   variant?: 'full' | 'studio' | 'ai',
 *   showLinks?: boolean,
 *   showPlans?: boolean,
 * }} props
 */
export default function EcosystemOverview({
  variant = 'full',
  showLinks = false,
  showPlans = false,
}) {
  const isAi = variant === 'ai';
  const isStudio = variant === 'studio';

  return (
    <div className="ecosystem-overview space-y-12">
      <section>
        <h2 className="ecosystem-section-title">Roadmap</h2>
        <p className="ecosystem-section-desc">
          Phase 1 proves the model internally. Phase 2 productizes AI for the world.
        </p>
        <EcosystemPhases />
      </section>

      <section>
        <h2 className="ecosystem-section-title">Three products, one company</h2>
        <p className="ecosystem-section-desc">
          Originals earns revenue. Studio produces. AI scales what Studio learned.
        </p>
        <EcosystemMap showLinks={showLinks} />
      </section>

      <section>
        <h2 className="ecosystem-section-title">Content lifecycle</h2>
        <p className="ecosystem-section-desc">
          Every documentary follows this path — Phase 2 extends the same AI outward.
        </p>
        <EcosystemFlow showLinks={showLinks} showPhaseBadges />
      </section>

      {(isStudio || variant === 'full') && (
        <section>
          <h2 className="ecosystem-section-title">Studio production pipeline</h2>
          <p className="ecosystem-section-desc">
            Eight stages inside {PRODUCTS.STUDIO.name} — team-only, never shown to subscribers.
          </p>
          <div className="ecosystem-pipeline">
            {STUDIO_PIPELINE.map((step, i) => (
              <Link
                key={step.id}
                to={step.path}
                className="ecosystem-pipeline-step"
              >
                <span className="ecosystem-pipeline-num">{i + 1}</span>
                <span>{step.label}</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="ecosystem-section-title">AI modules</h2>
        <p className="ecosystem-section-desc">
          Built in Studio first (Phase 1). Selected modules ship on {PRODUCTS.AI.name} (Phase 2).
        </p>
        <div className="ecosystem-ai-modules">
          {AI_MODULES.map((m) => (
            <article key={m.id} className="ecosystem-ai-module">
              <div className="ecosystem-ai-module-header">
                <h3>{m.name}</h3>
                <span className={`ecosystem-ai-module-phase ecosystem-ai-module-phase--${m.phase}`}>
                  P{m.phase}
                </span>
              </div>
              <p>{m.desc}</p>
              <div className="ecosystem-ai-module-tags">
                {m.studio && <span className="tag tag--studio">Studio</span>}
                {m.saas && <span className="tag tag--ai">AI SaaS</span>}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="ecosystem-section-title">Revenue flywheel</h2>
        <p className="ecosystem-section-desc">
          Each product strengthens the others — the loop compounds over time.
        </p>
        <ol className="ecosystem-flywheel">
          {REVENUE_FLYWHEEL.map((item, i) => (
            <li key={item.step} className="ecosystem-flywheel-step">
              <span className="ecosystem-flywheel-num">{i + 1}</span>
              <span className="ecosystem-flywheel-text">{item.step}</span>
              <span className={`ecosystem-flywheel-badge ${PRODUCT_STYLES[item.product]}`}>
                {PRODUCTS[item.product].shortName}
              </span>
            </li>
          ))}
        </ol>
      </section>

      {(showPlans || isAi) && (
        <section>
          <h2 className="ecosystem-section-title">UNTOLD AI subscriptions</h2>
          <p className="ecosystem-section-desc">Planned tiers for Phase 2 external creators.</p>
          <div className="ecosystem-plans">
            {AI_SAAS_PLANS.map((plan) => (
              <article
                key={plan.id}
                className={`ecosystem-plan ${plan.id === 'pro' ? 'ecosystem-plan--featured' : ''}`}
              >
                <h3>{plan.name}</h3>
                <p className="ecosystem-plan-price">{plan.price}</p>
                <ul>
                  {plan.features.map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>
      )}

      {isStudio && (
        <section className="ecosystem-cta-bar">
          <p>
            <strong>Phase 2 preview</strong> — share with investors & partners (not linked from public OTT nav).
          </p>
          <Link to={aiPath()} className="ecosystem-cta-link ecosystem-cta-link--ai">
            View UNTOLD AI landing →
          </Link>
        </section>
      )}

      {isAi && (
        <section className="ecosystem-cta-bar">
          <p>
            <strong>Phase 1 is live</strong> — our team runs this pipeline daily inside Studio.
          </p>
          <Link to={PRODUCTS.STUDIO.loginPath} className="ecosystem-cta-link ecosystem-cta-link--studio">
            UNTOLD STUDIO — Team login →
          </Link>
        </section>
      )}

      {variant === 'full' && !isStudio && !isAi && (
        <section className="ecosystem-cta-bar ecosystem-cta-bar--split">
          <Link to={studioPath('ecosystem')} className="ecosystem-cta-link ecosystem-cta-link--studio">
            Studio ecosystem map →
          </Link>
          <Link to={aiPath()} className="ecosystem-cta-link ecosystem-cta-link--ai">
            UNTOLD AI (Phase 2) →
          </Link>
        </section>
      )}
    </div>
  );
}
