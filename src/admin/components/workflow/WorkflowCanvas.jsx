import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import WorkflowCustomNode from './WorkflowCustomNode';

const nodeTypes = { workflow: WorkflowCustomNode };

function graphToFlow(graph, catalog = []) {
  const catalogMap = Object.fromEntries(catalog.map((n) => [n.type, n]));
  const nodes = (graph?.nodes || []).map((n) => {
    const meta = catalogMap[n.type] || {};
    return {
      id: n.id,
      type: 'workflow',
      position: n.position || { x: 0, y: 0 },
      data: {
        label: n.data?.label || meta.label || n.type,
        nodeType: n.type,
        icon: meta.icon || '⚙️',
        category: meta.category || 'agent',
        retries: n.data?.retries ?? meta.default_retries ?? 2,
        timeout_seconds: n.data?.timeout_seconds ?? meta.default_timeout,
        expression: n.data?.expression,
        max_iterations: n.data?.max_iterations,
        delay_seconds: n.data?.delay_seconds,
        ...n.data,
      },
    };
  });
  const edges = (graph?.edges || []).map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    sourceHandle: e.sourceHandle || e.source_handle || 'default',
    targetHandle: e.targetHandle || e.target_handle || 'in',
    animated: true,
    style: { stroke: 'rgba(212,175,55,0.6)' },
  }));
  return { nodes, edges };
}

function flowToGraph(nodes, edges, viewport) {
  return {
    nodes: nodes.map((n) => ({
      id: n.id,
      type: n.data.nodeType,
      position: n.position,
      data: {
        label: n.data.label,
        retries: n.data.retries,
        timeout_seconds: n.data.timeout_seconds,
        expression: n.data.expression,
        max_iterations: n.data.max_iterations,
        delay_seconds: n.data.delay_seconds,
      },
    })),
    edges: edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      sourceHandle: e.sourceHandle || 'default',
      targetHandle: e.targetHandle || 'in',
    })),
    viewport: viewport || { x: 0, y: 0, zoom: 1 },
  };
}

function WorkflowCanvasInner({
  initialGraph,
  catalog,
  nodeExecutions,
  onGraphChange,
  selectedNodeId,
  onSelectNode,
}) {
  const { nodes: initNodes, edges: initEdges } = useMemo(
    () => graphToFlow(initialGraph, catalog),
    [initialGraph, catalog],
  );
  const [nodes, setNodes, onNodesChange] = useNodesState(initNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initEdges);
  const rfInstance = useRef(null);

  useEffect(() => {
    if (!nodeExecutions) return;
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: { ...n.data, executionStatus: nodeExecutions[n.id]?.status },
      })),
    );
  }, [nodeExecutions, setNodes]);

  useEffect(() => {
    const { nodes: n, edges: e } = graphToFlow(initialGraph, catalog);
    setNodes(n);
    setEdges(e);
  }, [initialGraph, catalog, setNodes, setEdges]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [setEdges],
  );

  const onSelectionChange = useCallback(
    ({ nodes: sel }) => onSelectNode?.(sel[0]?.id || null),
    [onSelectNode],
  );

  const emitChange = useCallback(() => {
    if (!onGraphChange || !rfInstance.current) return;
    const vp = rfInstance.current.getViewport();
    onGraphChange(flowToGraph(nodes, edges, vp));
  }, [nodes, edges, onGraphChange]);

  useEffect(() => {
    emitChange();
  }, [nodes, edges, emitChange]);

  return (
    <div className="workflow-canvas h-[560px] rounded-xl border dark:border-white/10 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        onInit={(inst) => {
          rfInstance.current = inst;
        }}
        onSelectionChange={onSelectionChange}
        fitView
        proOptions={{ hideAttribution: true }}
        className="dark:bg-[#0a0a0c]"
      >
        <Background gap={20} color="rgba(255,255,255,0.04)" />
        <Controls className="!bg-black/60 !border-white/10" />
        <MiniMap
          className="!bg-black/60 !border-white/10"
          nodeColor={(n) => (n.data?.category === 'control' ? '#8b5cf6' : '#d4af37')}
        />
      </ReactFlow>
    </div>
  );
}

export default function WorkflowCanvas(props) {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

export { flowToGraph, graphToFlow };
