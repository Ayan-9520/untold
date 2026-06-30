import { Link } from 'react-router-dom';
import type { Project } from '@/types/studio';
import { formatStage } from './utils';
import { Badge } from '@/components/ui/badge';

interface RecentProductionsListProps {
  projects: Project[];
}

export default function RecentProductionsList({ projects }: RecentProductionsListProps) {
  if (!projects.length) {
    return <p className="text-sm text-studio-muted py-4 text-center">No active productions</p>;
  }

  return (
    <div className="divide-y divide-studio-border/60">
      {projects.map((p) => (
        <Link
          key={p.id}
          to="/projects"
          className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0 hover:bg-white/[0.02] -mx-2 px-2 rounded-lg transition-colors"
        >
          <div className="min-w-0">
            <p className="font-medium text-white text-sm truncate">{p.title}</p>
            <p className="text-xs text-studio-muted mt-0.5">
              {formatStage(p.stage)} · {p.assignee}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {p.publishing_status === 'published' && (
              <Badge variant="gold">Live</Badge>
            )}
            <Badge>{p.status}</Badge>
          </div>
        </Link>
      ))}
    </div>
  );
}
