import { PRODUCTS } from '../../config/ecosystem';

export default function StudioPageHeader({ section, title, description, children }) {
  return (
    <div className="studio-page-header">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-untold-gold mb-2">
          {PRODUCTS.STUDIO.name}{section ? ` · ${section}` : ''}
        </p>
        <h1 className="text-2xl sm:text-3xl font-bold dark:text-white light:text-black">{title}</h1>
        {description && (
          <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1 max-w-2xl">{description}</p>
        )}
      </div>
      {children && <div className="studio-page-header-actions">{children}</div>}
    </div>
  );
}
