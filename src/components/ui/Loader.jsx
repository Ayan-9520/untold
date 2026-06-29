export default function Loader({ label = 'Loading', fullScreen = false }) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-4
        ${fullScreen ? 'min-h-[50vh]' : 'py-12'}`}
      role="status"
      aria-live="polite"
      aria-label={label}
    >
      <div className="w-10 h-10 border-2 border-untold-gold border-t-transparent rounded-full animate-spin" />
      <p className="text-sm dark:text-untold-muted light:text-gray-500">{label}</p>
    </div>
  );
}
