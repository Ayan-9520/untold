import { useState, useCallback, useEffect } from 'react';
import SceneCard from './SceneCard';

function reorderById(list, fromId, toId) {
  if (fromId === toId) return list;
  const next = [...list];
  const fromIdx = next.findIndex((s) => s.id === fromId);
  const toIdx = next.findIndex((s) => s.id === toId);
  if (fromIdx < 0 || toIdx < 0) return list;
  const [item] = next.splice(fromIdx, 1);
  next.splice(toIdx, 0, item);
  return next.map((s, i) => ({ ...s, scene_number: i + 1, sort_order: i + 1 }));
}

export default function SceneList({ scenes, onUpdate, onDelete, onReorder }) {
  const [expandedId, setExpandedId] = useState(scenes[0]?.id ?? null);
  const [dragId, setDragId] = useState(null);
  const [dragOverId, setDragOverId] = useState(null);
  const [localScenes, setLocalScenes] = useState(scenes);

  useEffect(() => {
    if (!dragId) setLocalScenes(scenes);
  }, [scenes, dragId]);

  const handleUpdate = useCallback(
    (sceneId, patch) => {
      setLocalScenes((prev) => prev.map((s) => (s.id === sceneId ? { ...s, ...patch } : s)));
      onUpdate(sceneId, patch);
    },
    [onUpdate],
  );

  const handleDragStart = useCallback((e, id) => {
    setDragId(id);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', String(id));
  }, []);

  const handleDragOver = useCallback((e, id) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverId(id);
  }, []);

  const handleDrop = useCallback(
    (e, targetId) => {
      e.preventDefault();
      const fromId = dragId || Number(e.dataTransfer.getData('text/plain'));
      if (!fromId || fromId === targetId) {
        setDragId(null);
        setDragOverId(null);
        return;
      }
      const reordered = reorderById(localScenes, fromId, targetId);
      setLocalScenes(reordered);
      onReorder(reordered.map((s) => s.id));
      setDragId(null);
      setDragOverId(null);
    },
    [dragId, localScenes, onReorder],
  );

  const handleDragEnd = () => {
    setDragId(null);
    setDragOverId(null);
  };

  if (!localScenes.length) {
    return (
      <div className="rounded-xl border dark:border-white/10 p-10 text-center">
        <p className="text-sm dark:text-untold-muted">No scenes yet. Import from script or add a scene.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3" onDragEnd={handleDragEnd}>
      {localScenes.map((scene, index) => (
        <SceneCard
          key={scene.id}
          scene={scene}
          index={index}
          expanded={expandedId === scene.id}
          onToggle={(id) => setExpandedId((prev) => (prev === id ? null : id))}
          onUpdate={handleUpdate}
          onDelete={onDelete}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          isDragging={dragId === scene.id}
          dragOver={dragOverId === scene.id && dragId !== scene.id}
        />
      ))}
    </div>
  );
}
