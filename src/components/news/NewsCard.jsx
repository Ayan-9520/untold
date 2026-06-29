import { Link } from 'react-router-dom';

export default function NewsCard({ article, featured = false }) {
  const date = article.publishedAt
    ? new Date(article.publishedAt).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : '';

  const href = `/news/${article.id}`;

  return (
    <article
      className={`group rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 card-hover
        ${featured ? 'sm:col-span-2 lg:col-span-2' : ''}
        dark:bg-untold-surface light:bg-white`}
    >
      <Link to={href} className="block">
        <div className={`relative overflow-hidden ${featured ? 'aspect-[21/9]' : 'aspect-video'}`}>
          <img
            src={article.thumbnail}
            alt=""
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
          {article.breaking && (
            <span className="absolute top-3 left-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-600 text-white">
              Breaking
            </span>
          )}
          {article.trending && !article.breaking && (
            <span className="absolute top-3 left-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-untold-gold text-untold-dark">
              Trending
            </span>
          )}
          <span className="absolute top-3 right-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-black/60 text-white">
            {article.sport}
          </span>
          <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-5">
            <p className="text-xs text-white/70 mb-1">{date} · {article.author}</p>
            <h2 className={`font-display font-bold text-white group-hover:text-untold-gold-light transition-colors ${featured ? 'text-2xl sm:text-3xl' : 'text-lg'}`}>
              {article.title}
            </h2>
          </div>
        </div>
      </Link>
      {!featured && (
        <p className="p-4 text-sm dark:text-untold-white/75 light:text-gray-600 line-clamp-2">
          {article.excerpt}
        </p>
      )}
    </article>
  );
}
