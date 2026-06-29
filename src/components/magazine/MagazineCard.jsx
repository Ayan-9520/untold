import { Link } from 'react-router-dom';
import Badge from '../ui/Badge';

export default function MagazineCard({ issue }) {
  const accessBadge = {
    free: { variant: 'gold', label: 'Free Sample' },
    paid: { variant: 'outline', label: `₹${issue.priceINR}` },
    premium: { variant: 'premium', label: 'Premium' },
    vip: { variant: 'premium', label: 'VIP' },
  }[issue.access] || { variant: 'outline', label: 'Issue' };

  return (
    <Link to={`/magazine/${issue.id}`} className="group block card-premium">
      <article className="rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white">
        <div className="relative aspect-[3/4] overflow-hidden">
          <img
            src={issue.coverImage}
            alt={issue.title}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
          <div className="absolute top-3 left-3 flex gap-2">
            <Badge variant="gold" size="sm">{issue.quarter} {issue.year}</Badge>
            <Badge variant={accessBadge.variant} size="sm">{accessBadge.label}</Badge>
          </div>
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <p className="text-[10px] uppercase tracking-widest text-untold-gold-light font-semibold">{issue.theme}</p>
            <h3 className="font-display text-xl font-bold text-white mt-1 group-hover:text-untold-gold-light transition-colors">
              {issue.title}
            </h3>
            <p className="text-xs text-white/70 mt-1">{issue.pageCount} pages · PDF · Flipbook</p>
          </div>
        </div>
        <div className="px-4 py-3 flex flex-wrap gap-2 border-t dark:border-untold-border light:border-gray-100">
          <Badge variant="muted" size="sm">PDF</Badge>
          <Badge variant="muted" size="sm">Flipbook</Badge>
          <Badge variant="muted" size="sm">App</Badge>
        </div>
      </article>
    </Link>
  );
}
