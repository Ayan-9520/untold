import { PHASES } from '../../config/ecosystem';

const STATUS_STYLES = {
  active: 'ecosystem-phase--active',
  planned: 'ecosystem-phase--planned',
};

/**
 * Phase 1 vs Phase 2 roadmap cards.
 * @param {{ showMilestones?: boolean }} props
 */
export default function EcosystemPhases({ showMilestones = true }) {
  return (
    <div className="ecosystem-phases">
      {Object.values(PHASES).map((phase) => (
        <article
          key={phase.id}
          className={`ecosystem-phase ${STATUS_STYLES[phase.status] ?? ''}`}
        >
          <div className="ecosystem-phase-header">
            <div>
              <p className="ecosystem-phase-label">{phase.name}</p>
              <h3 className="ecosystem-phase-title">{phase.title}</h3>
              <p className="ecosystem-phase-tagline">{phase.tagline}</p>
            </div>
            <span className={`ecosystem-phase-badge ecosystem-phase-badge--${phase.status}`}>
              {phase.status === 'active' ? 'Live' : phase.timeline}
            </span>
          </div>
          <p className="ecosystem-phase-goal">{phase.goal}</p>
          {showMilestones && (
            <ul className="ecosystem-phase-milestones">
              {phase.milestones.map((m) => (
                <li key={m.label} className={m.done ? 'is-done' : ''}>
                  <span className="ecosystem-phase-check" aria-hidden>
                    {m.done ? '✓' : '○'}
                  </span>
                  {m.label}
                </li>
              ))}
            </ul>
          )}
        </article>
      ))}
    </div>
  );
}
