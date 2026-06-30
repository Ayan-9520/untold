import { Link, useParams } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPath } from '../../config/ecosystem';
import { usePublishingWorkspace } from '../features/publishing/hooks/usePublishing';
import PublishingWorkspace from '../features/publishing/components/PublishingWorkspace';

export default function PublishingWorkspacePage() {
  const { projectId } = useParams();
  const { data, isLoading, isError, refetch } = usePublishingWorkspace(projectId);

  if (isLoading) return <div className="h-96 skeleton rounded-xl" />;
  if (isError || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Publishing workspace unavailable</p>
        <button type="button" onClick={() => refetch()} className="text-sm text-untold-gold mt-2">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to={studioPath('content')} className="text-xs text-untold-gold hover:underline">← Publishing CMS</Link>
      <StudioPageHeader
        section="Publishing CMS"
        title={data.project_title}
        description={`Visibility: ${data.visibility} · ${data.jobs?.length || 0} publish jobs`}
      />
      <PublishingWorkspace workspace={data} />
    </div>
  );
}
