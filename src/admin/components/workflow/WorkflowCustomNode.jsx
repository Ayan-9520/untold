import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

const CATEGORY_STYLES = {
  agent: 'border-untold-gold/50 bg-untold-gold/5',
  control: 'border-violet-400/50 bg-violet-500/10',
};

function WorkflowCustomNode({ data, selected }) {
  const style = CATEGORY_STYLES[data.category] || CATEGORY_STYLES.agent;
  const status = data.executionStatus;

  return (
    <div
      className={`workflow-node px-3 py-2 rounded-lg border min-w-[140px] shadow-lg ${style} ${
        selected ? 'ring-2 ring-untold-gold' : ''
      } ${status === 'running' ? 'animate-pulse' : ''} ${status === 'completed' ? 'opacity-80' : ''} ${
        status === 'failed' ? 'border-red-400' : ''
      }`}
    >
      <Handle type="target" position={Position.Left} className="!bg-untold-gold !w-2 !h-2" />
      <div className="flex items-center gap-2">
        <span className="text-base">{data.icon}</span>
        <div className="min-w-0">
          <div className="text-xs font-semibold truncate">{data.label}</div>
          <div className="text-[10px] dark:text-untold-muted uppercase">{data.nodeType}</div>
        </div>
      </div>
      {status && (
        <div className="text-[9px] mt-1 uppercase tracking-wide dark:text-untold-muted">{status}</div>
      )}
      {data.nodeType === 'condition' && (
        <>
          <Handle type="source" id="true" position={Position.Right} style={{ top: '35%' }} className="!bg-emerald-400 !w-2 !h-2" />
          <Handle type="source" id="false" position={Position.Right} style={{ top: '65%' }} className="!bg-red-400 !w-2 !h-2" />
        </>
      )}
      {data.nodeType !== 'condition' && (
        <Handle type="source" id="default" position={Position.Right} className="!bg-untold-gold !w-2 !h-2" />
      )}
    </div>
  );
}

export default memo(WorkflowCustomNode);
