import { Link, useParams } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPath } from '../../config/ecosystem';
import TimelineEditor from '../features/timeline/components/TimelineEditor';
import {
  useTimelineEditor,
  useTimelineExports,
  useTimelineWorkspace,
} from '../features/timeline/hooks/useTimeline';

export default function TimelineWorkspacePage() {
  const { projectId } = useParams();
  const { data, isLoading, isError, refetch } = useTimelineWorkspace(projectId);
  const { data: exports } = useTimelineExports(projectId);
  const { engine, snapshot, saveNow, saving, lastSaved, createExport } = useTimelineEditor(projectId, data);

  if (isLoading) return <div className="h-96 skeleton rounded-xl" />;
  if (isError || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Timeline workspace unavailable</p>
        <button type="button" onClick={() => refetch()} className="text-sm text-untold-gold mt-2">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to={studioPath('timeline')} className="text-xs text-untold-gold hover:underline">← Timeline Editor</Link>

      <StudioPageHeader
        section="Timeline Editor"
        title={data.project_title}
        description={`${data.track_count} tracks · ${data.clip_count} clips · ${data.duration.toFixed(0)}s · v${data.version}`}
      />

      <TimelineEditor
        engine={engine}
        snapshot={snapshot}
        saveNow={saveNow}
        saving={saving}
        lastSaved={lastSaved}
        exports={exports}
        onExport={(opts) => createExport.mutate(opts)}
        exporting={createExport.isPending}
      />
    </div>
  );
}
