import { useState } from 'react';
import { Link } from 'react-router-dom';
import { PLATFORM_ROADMAP } from '../../config/ecosystem';

function PhaseNode({ phase, isLast }) {
  const inner = (
    <div
      className={`platform-roadmap-node ${
        phase.done !== false ? 'platform-roadmap-node--done' : 'platform-roadmap-node--pending'
      }`}
    >
      <span className="platform-roadmap-phase-num">Phase {phase.id ?? `${phase.from}–${phase.to}`}</span>
      <span className="platform-roadmap-label">{phase.label}</span>
      {phase.done && <span className="platform-roadmap-check" aria-label="Complete">✅</span>}
      {phase.description && (
        <p className="platform-roadmap-desc">{phase.description}</p>
      )}
    </div>
  );

  return (
    <li className="platform-roadmap-item">
      {phase.path ? (
        <Link to={phase.path} className="platform-roadmap-link">
          {inner}
        </Link>
      ) : (
        inner
      )}
      {!isLast && <span className="platform-roadmap-arrow" aria-hidden>↓</span>}
    </li>
  );
}

/**
 * Vertical platform roadmap — Phases 1–23 Studio + 24–37 AI platform.
 */
export default function PlatformRoadmap({ compact = false }) {
  const [expanded, setExpanded] = useState(!compact);

  return (
    <div className="platform-roadmap">
      <ol className="platform-roadmap-list">
        {PLATFORM_ROADMAP.map((entry, i) => {
          const isLast = i === PLATFORM_ROADMAP.length - 1;

          if (entry.type === 'group') {
            return (
              <li key={entry.id} className="platform-roadmap-item">
                <button
                  type="button"
                  onClick={() => setExpanded((v) => !v)}
                  className="platform-roadmap-group w-full text-left"
                >
                  <span className="platform-roadmap-phase-num">
                    Phase {entry.from}–{entry.to}
                  </span>
                  <span className="platform-roadmap-label">{entry.label}</span>
                  <span className="platform-roadmap-check" aria-hidden>✅</span>
                  <span className="platform-roadmap-expand text-[10px] dark:text-untold-muted ml-2">
                    {expanded ? 'Hide details' : 'Show all 23'}
                  </span>
                </button>
                {expanded && (
                  <ul className="platform-roadmap-sublist mt-2 space-y-1 pl-3 border-l dark:border-white/10">
                    {entry.phases.map((p) => (
                      <li key={p.id} className="text-xs dark:text-untold-muted flex items-center gap-2">
                        <span className="text-emerald-400">✓</span>
                        {p.path ? (
                          <Link to={p.path} className="hover:text-untold-gold">{p.label}</Link>
                        ) : (
                          p.label
                        )}
                      </li>
                    ))}
                  </ul>
                )}
                {!isLast && <span className="platform-roadmap-arrow" aria-hidden>↓</span>}
              </li>
            );
          }

          return <PhaseNode key={entry.id} phase={entry} isLast={isLast} />;
        })}
      </ol>
    </div>
  );
}
