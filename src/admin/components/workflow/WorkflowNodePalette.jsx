export default function WorkflowNodePalette({ catalog, onAdd }) {
  const agents = catalog.filter((n) => n.category === 'agent');
  const controls = catalog.filter((n) => n.category === 'control');

  const Item = ({ item }) => (
    <button
      type="button"
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData('application/workflow-node', JSON.stringify(item));
        e.dataTransfer.effectAllowed = 'move';
      }}
      onClick={() => onAdd(item)}
      className="workflow-palette-item flex items-center gap-2 w-full text-left px-2 py-1.5 rounded-md text-xs hover:bg-white/5 border border-transparent hover:border-white/10"
    >
      <span>{item.icon}</span>
      <span>{item.label}</span>
    </button>
  );

  return (
    <div className="workflow-palette space-y-4">
      <div>
        <h4 className="text-[10px] uppercase tracking-wider dark:text-untold-muted mb-2">Agents</h4>
        <div className="space-y-0.5">{agents.map((item) => <Item key={item.type} item={item} />)}</div>
      </div>
      <div>
        <h4 className="text-[10px] uppercase tracking-wider dark:text-untold-muted mb-2">Control</h4>
        <div className="space-y-0.5">{controls.map((item) => <Item key={item.type} item={item} />)}</div>
      </div>
    </div>
  );
}
