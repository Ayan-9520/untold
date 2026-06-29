import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import EcosystemOverview from '../../components/ecosystem/EcosystemOverview';
import { PRODUCTS, aiPath } from '../../config/ecosystem';

export default function EcosystemPage() {
  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Ecosystem"
        title="Phase 1 · Phase 2 · Complete Map"
        description={`How ${PRODUCTS.ORIGINALS.name}, ${PRODUCTS.STUDIO.name}, and ${PRODUCTS.AI.name} connect. Internal reference — not shown on public OTT nav.`}
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
