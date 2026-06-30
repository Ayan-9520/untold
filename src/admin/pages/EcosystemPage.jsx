import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import EcosystemOverview from '../../components/ecosystem/EcosystemOverview';
import { PRODUCTS, aiPath } from '../../config/ecosystem';

export default function EcosystemPage() {
  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Ecosystem"
        title="Platform Roadmap · Phases 1–37"
        description="Studio features (1–23) and AI platform layers (24–37) — how the full stack is built."
      >
        <Link
          to={aiPath()}
          className="text-sm px-4 py-2 rounded-lg border border-purple-400/40 text-purple-300 hover:bg-purple-500/10 transition-colors"
        >
          UNTOLD AI landing →
        </Link>
      </StudioPageHeader>

      <EcosystemOverview variant="studio" showLinks />
    </div>
  );
}
