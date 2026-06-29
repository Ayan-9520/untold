import { Link } from 'react-router-dom';
import SEO from '../components/SEO';

const POSTS = [
  {
    id: 'blog-ai-storytelling',
    title: 'How AI Is Rewriting Sports Storytelling',
    excerpt: 'UNTOLD\'s AI agents now handle 85% of localization, news summaries, and live commentary — with human editors approving every publish.',
    date: '2026-03-15',
    category: 'Platform',
    image: 'https://images.unsplash.com/photo-1504711434969-e33886168f1c?w=800&q=80',
  },
  {
    id: 'blog-fan-wars',
    title: 'Fan Wars: India vs Pakistan Breaks Records',
    excerpt: 'Over 87,000 votes cast in 48 hours as UNTOLD\'s fan community battles for bragging rights.',
    date: '2026-03-10',
    category: 'Community',
    image: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=800&q=80',
  },
  {
    id: 'blog-dhoni-doc',
    title: 'Behind the Scenes: Rise of Dhoni',
    excerpt: 'Director\'s cut insights from UNTOLD Originals\' most-watched cricket documentary.',
    date: '2026-03-01',
    category: 'Originals',
    image: 'https://images.unsplash.com/photo-1540747913346-19a32ad3b0f2?w=800&q=80',
  },
];

export default function Blog() {
  return (
    <>
      <SEO title="Blog" description="UNTOLD blog — sports media, AI, and fan culture" path="/blog" />
      <section className="pt-28 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.3em] text-untold-gold mb-2">UNTOLD Blog</p>
            <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
              Stories About Stories
            </h1>
            <p className="mt-3 text-sm dark:text-untold-muted light:text-gray-600">
              Platform updates, behind-the-scenes, and sports media intelligence.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {POSTS.map((post) => (
              <article key={post.id} className="rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 dark:bg-untold-surface light:bg-white card-premium group">
                <div className="aspect-video overflow-hidden">
                  <img src={post.image} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
                </div>
                <div className="p-5">
                  <p className="text-xs text-untold-gold font-semibold uppercase">{post.category} · {post.date}</p>
                  <h2 className="font-display text-lg font-bold dark:text-untold-white light:text-black mt-2 group-hover:text-untold-gold transition-colors">
                    {post.title}
                  </h2>
                  <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600 line-clamp-2">{post.excerpt}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
