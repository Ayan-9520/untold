import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronRightIcon } from '../icons';

export default function SectionHeader({ title, subtitle, viewAllLink, viewAllText }) {
  const { t } = useTranslation();
  const viewAllLabel = viewAllText || t('common.viewAll');

  return (
    <div className="flex items-end justify-between mb-6 px-4 sm:px-6 lg:px-8">
      <div>
        <h2 className="font-display text-2xl sm:text-3xl font-bold tracking-tight dark:text-untold-white light:text-black">
          {title}
        </h2>
        {subtitle && (
          <p className="mt-1 text-sm dark:text-untold-muted light:text-gray-500">{subtitle}</p>
        )}
      </div>
      {viewAllLink && (
        <Link
          to={viewAllLink}
          className="flex items-center gap-1 text-sm font-medium text-untold-gold dark:hover:text-untold-gold-light light:text-untold-gold-dark light:hover:text-untold-gold transition-colors shrink-0"
        >
          {viewAllLabel}
          <ChevronRightIcon className="w-4 h-4" />
        </Link>
      )}
    </div>
  );
}
