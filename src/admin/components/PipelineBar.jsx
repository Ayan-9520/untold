import { Link } from 'react-router-dom';
import { STUDIO_PIPELINE } from '../../config/ecosystem';

export default function PipelineBar({ activeStep }) {
  return (
    <div className="studio-pipeline-bar" role="list" aria-label="Production pipeline">
      {STUDIO_PIPELINE.map((step, i) => {
        const isActive = activeStep === step.id;
        return (
          <div key={step.id} className="studio-pipeline-bar-item" role="listitem">
            {i > 0 && <span className="studio-pipeline-bar-arrow" aria-hidden>→</span>}
            <Link
              to={step.path}
              className={`studio-pipeline-bar-chip${isActive ? ' studio-pipeline-bar-chip--active' : ''}`}
            >
              <span className="studio-pipeline-bar-num">{i + 1}</span>
              {step.label}
            </Link>
          </div>
        );
      })}
    </div>
  );
}
