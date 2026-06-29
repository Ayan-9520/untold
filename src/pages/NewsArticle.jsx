import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import SEO from '../components/SEO';
import Loader from '../components/ui/Loader';
import newsApi from '../api/news';

export default function NewsArticle() {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    newsApi.get(id).then(({ data }) => {
      if (active) {
        setArticle(data);
        setLoading(false);
      }
    });
    return () => { active = false; };
  }, [id]);

  if (loading) return <Loader fullScreen label="Loading article" />;
  if (!article) {
    return (
      <div className="pt-32 text-center dark:text-untold-muted">
        <p>Article not found.</p>
        <Link to="/news" className="text-untold-gold mt-4 inline-block">Back to News</Link>
      </div>
    );
  }

  const date = article.publishedAt
    ? new Date(article.publishedAt).toLocaleDateString('en-US', { dateStyle: 'long' })
    : '';

  return (
    <>
      <SEO
        title={article.seoTitle || article.title}
        description={article.seoDescription || article.excerpt}
        path={`/news/${article.id}`}
      />

      <article className="pt-28 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl">
          <Link to="/news" className="text-sm text-untold-gold hover:underline mb-6 inline-block">
            ← Back to News
          </Link>

          <div className="flex flex-wrap gap-2 mb-4">
            <span className="text-xs font-bold uppercase tracking-wider text-untold-gold">{article.sport}</span>
            {article.breaking && (
              <span className="text-xs font-bold uppercase tracking-wider text-red-500">Breaking</span>
            )}
          </div>

          <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black mb-4">
            {article.title}
          </h1>

          <p className="text-sm dark:text-untold-muted light:text-gray-500 mb-8">
            {date} · {article.author}
          </p>

          {article.thumbnail && (
            <img
              src={article.thumbnail}
              alt=""
              className="w-full rounded-xl aspect-video object-cover mb-8"
            />
          )}

          <div className="prose prose-invert max-w-none dark:text-untold-white/90 light:text-gray-800">
            {(article.content || article.excerpt || '').split('\n').map((para, i) => (
              <p key={i} className="mb-4 text-base leading-relaxed">{para}</p>
            ))}
          </div>
        </div>
      </article>
    </>
  );
}
