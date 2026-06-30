import { STUDIO_PRODUCTION_PIPELINE } from '../../config/ecosystem';

/** Vertical Idea → Analytics flow diagram */
export default function StudioProductionFlow({ compact = false }) {
  return (
    <div className={`rounded-xl border dark:border-white/10 p-4 dark:bg-untold-card/20 ${compact ? '' : 'max-w-xs mx-auto'}`}>
      <ol className="space-y-0">
        {STUDIO_PRODUCTION_PIPELINE.map((step, i) => (
          <li key={step.id} className="flex flex-col items-center">
            <div className="w-full rounded-lg border dark:border-white/10 px-3 py-2 text-center text-xs font-medium dark:text-white bg-white/[0.02]">
              {step.label}
            </div>
            {i < STUDIO_PRODUCTION_PIPELINE.length - 1 && (
              <span className="text-untold-gold py-1 text-sm" aria-hidden>↓</span>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
