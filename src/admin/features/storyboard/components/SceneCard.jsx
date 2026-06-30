import { SHOT_TYPES, MOODS, TRANSITIONS } from '../constants';

const STATUS_OPTIONS = [
  { value: 'draft', label: 'Draft' },
  { value: 'review', label: 'In review' },
  { value: 'approved', label: 'Approved' },
  { value: 'locked', label: 'Locked' },
];

const CAMERA_ANGLES = ['Wide shot', 'Medium shot', 'Close-up', 'Establishing', 'Over-the-shoulder', 'POV', 'Aerial'];
const CAMERA_MOVEMENTS = ['Static', 'Pan left', 'Pan right', 'Tilt up', 'Tilt down', 'Dolly in', 'Dolly out', 'Drone rise', 'Handheld'];
const LIGHTING = ['Natural', 'Soft key', 'Hard key', 'Golden hour', 'Low key', 'High key', 'Backlit'];

function Field({ label, children }) {
  return (
    <label className="block space-y-1">
      <span className="text-[10px] uppercase tracking-wider dark:text-untold-muted">{label}</span>
      {children}
    </label>
  );
}

const inputClass = 'w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white';

export default function SceneCard({
  scene,
  index,
  expanded,
  onToggle,
  onUpdate,
  onDelete,
  onDragStart,
  onDragOver,
  onDrop,
  isDragging,
  dragOver,
}) {
  const set = (field, value) => onUpdate(scene.id, { [field]: value });

  return (
    <article
      draggable
      onDragStart={(e) => onDragStart(e, scene.id)}
      onDragOver={(e) => onDragOver(e, scene.id)}
      onDrop={(e) => onDrop(e, scene.id)}
      className={`rounded-xl border transition-all ${
        isDragging ? 'opacity-40 scale-[0.98]' : ''
      } ${dragOver ? 'border-untold-gold/60 ring-1 ring-untold-gold/30' : 'dark:border-white/10'} dark:bg-untold-card/40`}
    >
      <header
        className="flex items-center gap-3 px-4 py-3 cursor-grab active:cursor-grabbing"
        onClick={() => onToggle(scene.id)}
      >
        <span className="text-untold-gold font-mono text-sm w-8 shrink-0" title="Drag to reorder">⋮⋮</span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold dark:text-white truncate">
            Scene {scene.scene_number}
            {scene.visual_prompt ? ` — ${scene.visual_prompt.slice(0, 60)}` : ''}
          </p>
          <p className="text-[10px] dark:text-untold-muted mt-0.5">
            {scene.duration_seconds}s · {scene.status}
            {scene.shot_type ? ` · ${scene.shot_type}` : scene.camera_angle ? ` · ${scene.camera_angle}` : ''}
            {scene.mood ? ` · ${scene.mood}` : ''}
          </p>
        </div>
        <span className="text-xs dark:text-untold-muted">{expanded ? '▲' : '▼'}</span>
      </header>

      {expanded && (
        <div className="px-4 pb-4 pt-1 border-t dark:border-white/10 grid gap-3 sm:grid-cols-2">
          <Field label="Duration (seconds)">
            <input
              type="number"
              min={0}
              max={3600}
              value={scene.duration_seconds}
              onChange={(e) => set('duration_seconds', Number(e.target.value))}
              className={inputClass}
            />
          </Field>
          <Field label="Status">
            <select value={scene.status} onChange={(e) => set('status', e.target.value)} className={inputClass}>
              {STATUS_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </Field>
          <Field label="Visual prompt">
            <textarea
              rows={2}
              value={scene.visual_prompt || ''}
              onChange={(e) => set('visual_prompt', e.target.value)}
              className={`${inputClass} sm:col-span-2`}
            />
          </Field>
          <Field label="Narration">
            <textarea
              rows={3}
              value={scene.narration || ''}
              onChange={(e) => set('narration', e.target.value)}
              className={`${inputClass} sm:col-span-2`}
            />
          </Field>
          <Field label="Dialogue">
            <textarea
              rows={2}
              value={scene.dialogue || ''}
              onChange={(e) => set('dialogue', e.target.value)}
              className={`${inputClass} sm:col-span-2`}
              placeholder="Interview lines, quoted speech…"
            />
          </Field>
          <Field label="Shot type">
            <select value={scene.shot_type || ''} onChange={(e) => set('shot_type', e.target.value)} className={inputClass}>
              <option value="">Select…</option>
              {SHOT_TYPES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </Field>
          <Field label="Camera angle">
            <select
              value={scene.camera_angle || ''}
              onChange={(e) => set('camera_angle', e.target.value)}
              className={inputClass}
            >
              <option value="">Select…</option>
              {CAMERA_ANGLES.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </Field>
          <Field label="Camera movement">
            <select
              value={scene.camera_movement || ''}
              onChange={(e) => set('camera_movement', e.target.value)}
              className={inputClass}
            >
              <option value="">Select…</option>
              {CAMERA_MOVEMENTS.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </Field>
          <Field label="Lighting">
            <select
              value={scene.lighting || ''}
              onChange={(e) => set('lighting', e.target.value)}
              className={inputClass}
            >
              <option value="">Select…</option>
              {LIGHTING.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </Field>
          <Field label="Environment">
            <input
              value={scene.environment || ''}
              onChange={(e) => set('environment', e.target.value)}
              className={inputClass}
              placeholder="Stadium, archive room…"
            />
          </Field>
          <Field label="Mood">
            <select value={scene.mood || ''} onChange={(e) => set('mood', e.target.value)} className={inputClass}>
              <option value="">Select…</option>
              {MOODS.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </Field>
          <Field label="Transition">
            <select value={scene.transition || ''} onChange={(e) => set('transition', e.target.value)} className={inputClass}>
              <option value="">Select…</option>
              {TRANSITIONS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </Field>
          <Field label="Reference image URL">
            <input
              value={scene.reference_image_url || ''}
              onChange={(e) => set('reference_image_url', e.target.value)}
              className={`${inputClass} sm:col-span-2`}
              placeholder="https://…"
            />
          </Field>
          {scene.reference_image_url && (
            <div className="sm:col-span-2">
              <img
                src={scene.reference_image_url}
                alt={`Scene ${scene.scene_number} reference`}
                className="max-h-32 rounded-lg border dark:border-white/10 object-cover"
                onError={(e) => { e.currentTarget.style.display = 'none'; }}
              />
            </div>
          )}
          <div className="sm:col-span-2 flex justify-end">
            <button
              type="button"
              onClick={() => onDelete(scene.id)}
              className="text-xs text-red-400 hover:underline"
            >
              Delete scene
            </button>
          </div>
        </div>
      )}
    </article>
  );
}
