import { useCallback, useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import WorkflowCanvas from '../components/workflow/WorkflowCanvas';
import WorkflowNodePalette from '../components/workflow/WorkflowNodePalette';
import { studioPlatform } from '../api/adminApi';
import { studioPath } from '../../config/ecosystem';

const workflowBuilderKey = ['workflow-builder'];

function NodeInspector({ node, catalog, onChange }) {
  if (!node) {
    return <p className="text-xs dark:text-untold-muted">Select a node to configure retries, timeouts, and conditions.</p>;
  }
  const meta = catalog.find((c) => c.type === node.data?.nodeType) || {};

  return (
    <div className="space-y-3 text-sm">
      <div>
        <div className="font-medium">{node.data?.label}</div>
        <div className="text-[10px] uppercase dark:text-untold-muted">{node.data?.nodeType}</div>
      </div>
      <label className="block">
        <span className="text-xs dark:text-untold-muted">Label</span>
        <input
          className="studio-input w-full mt-1"
          value={node.data?.label || ''}
          onChange={(e) => onChange(node.id, { label: e.target.value })}
        />
      </label>
      {meta.category === 'agent' && (
        <>
          <label className="block">
            <span className="text-xs dark:text-untold-muted">Retries</span>
            <input
              type="number"
              min={0}
              max={10}
              className="studio-input w-full mt-1"
              value={node.data?.retries ?? 2}
              onChange={(e) => onChange(node.id, { retries: Number(e.target.value) })}
            />
          </label>
          <label className="block">
            <span className="text-xs dark:text-untold-muted">Timeout (seconds)</span>
            <input
              type="number"
              min={0}
              className="studio-input w-full mt-1"
              value={node.data?.timeout_seconds ?? ''}
              onChange={(e) => onChange(node.id, { timeout_seconds: e.target.value ? Number(e.target.value) : null })}
            />
          </label>
        </>
      )}
      {node.data?.nodeType === 'condition' && (
        <label className="block">
          <span className="text-xs dark:text-untold-muted">Expression field</span>
          <input
            className="studio-input w-full mt-1"
            placeholder="research, script, video…"
            value={node.data?.expression || ''}
            onChange={(e) => onChange(node.id, { expression: e.target.value })}
          />
        </label>
      )}
      {node.data?.nodeType === 'loop' && (
        <label className="block">
          <span className="text-xs dark:text-untold-muted">Max iterations</span>
          <input
            type="number"
            min={1}
            max={20}
            className="studio-input w-full mt-1"
            value={node.data?.max_iterations ?? 3}
            onChange={(e) => onChange(node.id, { max_iterations: Number(e.target.value) })}
          />
        </label>
      )}
      {node.data?.nodeType === 'delay' && (
        <label className="block">
          <span className="text-xs dark:text-untold-muted">Delay seconds</span>
          <input
            type="number"
            min={0}
            className="studio-input w-full mt-1"
            value={node.data?.delay_seconds ?? 0}
            onChange={(e) => onChange(node.id, { delay_seconds: Number(e.target.value) })}
          />
        </label>
      )}
    </div>
  );
}

export default function WorkflowBuilderPage() {
  const { definitionId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const isNew = !definitionId || definitionId === 'new';

  const [name, setName] = useState('Untitled Workflow');
  const [description, setDescription] = useState('');
  const [graph, setGraph] = useState({ nodes: [], edges: [], viewport: { x: 0, y: 0, zoom: 1 } });
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [topic, setTopic] = useState('');
  const [changelog, setChangelog] = useState('');

  const { data: catalogData } = useQuery({
    queryKey: [...workflowBuilderKey, 'catalog'],
    queryFn: () => studioPlatform.getWorkflowNodeCatalog(),
  });
  const catalog = catalogData?.nodes || [];

  const { data: definition } = useQuery({
    queryKey: [...workflowBuilderKey, 'definition', definitionId],
    queryFn: () => studioPlatform.getWorkflowDefinition(Number(definitionId)),
    enabled: !isNew,
  });

  useEffect(() => {
    if (definition) {
      setName(definition.name);
      setDescription(definition.description || '');
      if (definition.current_version?.graph) setGraph(definition.current_version.graph);
    }
  }, [definition]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (isNew) {
        const created = await studioPlatform.createWorkflowDefinition({
          name,
          description,
          graph,
        });
        await studioPlatform.createWorkflowVersion(created.id, { graph, changelog: changelog || 'Initial save' });
        return created;
      }
      await studioPlatform.createWorkflowVersion(Number(definitionId), {
        graph,
        changelog: changelog || `Version save ${new Date().toLocaleString()}`,
      });
      return definition;
    },
    onSuccess: (result) => {
      qc.invalidateQueries({ queryKey: workflowBuilderKey });
      if (isNew && result?.id) navigate(studioPath(`workflows/builder/${result.id}`), { replace: true });
    },
  });

  const runMutation = useMutation({
    mutationFn: () =>
      studioPlatform.executeWorkflowDefinition(Number(definitionId), {
        topic: topic || name,
        auto_run: true,
      }),
    onSuccess: (run) => navigate(studioPath(`workflows/runs/${run.id}`)),
  });

  const addNode = useCallback(
    (item) => {
      const id = `n_${item.type}_${Date.now()}`;
      setGraph((g) => ({
        ...g,
        nodes: [
          ...g.nodes,
          {
            id,
            type: item.type,
            position: { x: 80 + g.nodes.length * 40, y: 80 + g.nodes.length * 30 },
            data: {
              label: item.label,
              retries: item.default_retries ?? 2,
              timeout_seconds: item.default_timeout,
            },
          },
        ],
      }));
    },
    [],
  );

  const selectedNode = useMemo(() => {
    const n = graph.nodes.find((nd) => nd.id === selectedNodeId);
    if (!n) return null;
    return {
      id: n.id,
      data: {
        label: n.data?.label,
        nodeType: n.type,
        ...n.data,
      },
    };
  }, [graph.nodes, selectedNodeId]);

  const updateNodeData = useCallback((nodeId, patch) => {
    setGraph((g) => ({
      ...g,
      nodes: g.nodes.map((n) => (n.id === nodeId ? { ...n, data: { ...n.data, ...patch } } : n)),
    }));
  }, []);

  return (
    <div className="studio-page">
      <StudioPageHeader
        title={isNew ? 'New Workflow' : name}
        description="Visual production pipeline — drag nodes, connect stages, version, and execute"
        actions={
          <div className="flex gap-2 flex-wrap">
            <Link to={studioPath('workflows')} className="studio-btn studio-btn--ghost text-sm">
              ← Dashboard
            </Link>
            <button type="button" className="studio-btn studio-btn--secondary text-sm" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Saving…' : 'Save version'}
            </button>
            {!isNew && (
              <button type="button" className="studio-btn studio-btn--primary text-sm" onClick={() => runMutation.mutate()} disabled={!topic || runMutation.isPending}>
                Run workflow
              </button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mt-4">
        <aside className="lg:col-span-2 studio-card p-3">
          <WorkflowNodePalette catalog={catalog} onAdd={addNode} />
        </aside>

        <div className="lg:col-span-7 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="text-xs dark:text-untold-muted">Workflow name</span>
              <input className="studio-input w-full mt-1" value={name} onChange={(e) => setName(e.target.value)} />
            </label>
            {!isNew && (
              <label className="block">
                <span className="text-xs dark:text-untold-muted">Run topic</span>
                <input className="studio-input w-full mt-1" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Documentary topic…" />
              </label>
            )}
          </div>
          <WorkflowCanvas
            initialGraph={graph}
            catalog={catalog}
            onGraphChange={setGraph}
            selectedNodeId={selectedNodeId}
            onSelectNode={setSelectedNodeId}
          />
          <input
            className="studio-input w-full text-xs"
            placeholder="Version changelog (optional)"
            value={changelog}
            onChange={(e) => setChangelog(e.target.value)}
          />
        </div>

        <aside className="lg:col-span-3 studio-card p-4 space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-2">Node inspector</h3>
            <NodeInspector node={selectedNode} catalog={catalog} onChange={updateNodeData} />
          </div>
          {!isNew && definition?.current_version && (
            <div className="text-xs dark:text-untold-muted border-t dark:border-white/10 pt-3">
              Version v{definition.current_version.version} · {definition.status}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
