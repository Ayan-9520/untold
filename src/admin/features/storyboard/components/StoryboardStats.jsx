export default function StoryboardStats({ sceneCount, totalDuration }) {
  const mins = Math.floor(totalDuration / 60);
  const secs = totalDuration % 60;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <div className="ai-stat-card text-center">
        <p className="text-2xl font-bold text-untold-gold">{sceneCount}</p>
        <p className="text-xs dark:text-untold-muted mt-1">Scenes</p>
      </div>
      <div className="ai-stat-card text-center">
        <p className="text-2xl font-bold text-untold-gold">{mins}:{String(secs).padStart(2, '0')}</p>
        <p className="text-xs dark:text-untold-muted mt-1">Total runtime</p>
      </div>
      <div className="ai-stat-card text-center col-span-2 sm:col-span-1">
        <p className="text-2xl font-bold text-untold-gold">↕</p>
        <p className="text-xs dark:text-untold-muted mt-1">Drag to reorder</p>
      </div>
    </div>
  );
}
