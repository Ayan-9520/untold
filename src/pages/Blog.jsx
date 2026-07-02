import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';
import Loader from '../components/ui/Loader';
import newsApi from '../api/news';

export default function Blog() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    newsApi.list({ page: 1, page_size: 12 })
      .then(({ items }) => setPosts(items))
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader fullScreen label="Loading blog" />;

  return (
    <>
      <SEO title="Blog" description="UNTOLD blog — global sports storytelling, biopics, and fan culture" path="/blog" />
      <section className="pt-28 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.3em] text-untold-gold mb-2">UNTOLD Blog</p>
            <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
              Stories About Stories
            </h1>
            <p className="mt-3 text-sm dark:text-untold-muted light:text-gray-600">
              Biopics, rivalries, documentaries, and sports media intelligence from every arena.
            </p>
          </div>
          {posts.length === 0 ? (
            <p className="text-center py-12 text-sm dark:text-untold-muted light:text-gray-500">No articles published yet.</p>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {posts.map((post) => (
                <Link key={post.id} to={`/news/${post.id}`} className="block group">
                  <article className="rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white card-premium h-full">
                    {post.thumbnail && (
                      <div className="aspect-video overflow-hidden">
                        <img src={post.thumbnail} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
                      </div>
                    )}
                    <div className="p-5">
                      <p className="text-xs text-untold-gold font-semibold uppercase">
                        {post.category || post.sport || 'Editorial'}
                        {post.publishedAt ? ` · ${new Date(post.publishedAt).toLocaleDateString()}` : ''}
                      </p>
                      <h2 className="font-display text-lg font-bold dark:text-untold-white light:text-black mt-2 group-hover:text-untold-gold transition-colors">
                        {post.title}
                      </h2>
                      <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600 line-clamp-2">{post.excerpt}</p>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
