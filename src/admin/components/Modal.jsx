import { XIcon } from './AdminIcons';

export default function Modal({ open, onClose, title, children, wide }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div
        className={`relative w-full ${wide ? 'max-w-2xl' : 'max-w-lg'} max-h-[90vh] overflow-y-auto
          rounded-2xl dark:bg-untold-surface light:bg-white shadow-2xl animate-scale-in`}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b dark:border-white/10 light:border-gray-100">
          <h2 className="text-lg font-semibold dark:text-untold-white light:text-black">{title}</h2>
          <button onClick={onClose} className="p-1 rounded-lg hover:dark:bg-white/10 hover:light:bg-black/5">
            <XIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}
