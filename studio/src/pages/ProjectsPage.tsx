import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studioApi } from '@/api/studio';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function ProjectsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['projects'], queryFn: () => studioApi.projects() });

  const create = useMutation({
    mutationFn: () => studioApi.createProject({ title: `Production ${Date.now()}`, stage: 'research' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  });

  const publish = useMutation({
    mutationFn: (id: number) => studioApi.publishProject(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  });

  if (isLoading) return <div className="h-48 rounded-xl bg-studio-card animate-pulse" />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Projects</h1>
        <Button variant="gold" onClick={() => create.mutate()} disabled={create.isPending}>
          New Project
        </Button>
      </div>
      <div className="grid gap-3">
        {data?.items.map((p) => (
          <Card key={p.id} className="flex justify-between items-center gap-4">
            <div>
              <p className="font-semibold text-white">{p.title}</p>
              <p className="text-xs text-studio-muted">{p.slug} · {p.stage}</p>
            </div>
            {p.publishing_status !== 'published' && (
              <Button variant="outline" onClick={() => publish.mutate(p.id)} disabled={publish.isPending}>
                Publish to Originals
              </Button>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
