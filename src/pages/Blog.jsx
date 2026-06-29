import { Link } from 'react-router-dom';
import SEO from '../components/SEO';

const POSTS = [
  {
    id: 'blog-multi-sport',
    title: 'Why UNTOLD Covers Every Arena — Not Just One Sport',
    excerpt: 'From biopics and rivalries to Olympic stories and boxing legends — how we built a global sports storytelling platform.',
    date: '2026-03-18',
    category: 'Platform',
    image: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=800&q=80',
  },
  {
    id: 'blog-biopics',
    title: 'The Rise of Sports Biopics in 2026',
    excerpt: 'Jordan, Ali, Senna, Messi — audiences want depth. UNTOLD Originals on the biopic boom across football, F1, and beyond.',
    date: '2026-03-12',
    category: 'Originals',
    image: 'https://images.unsplash.com/photo-1519861531473-9200292dcfe3?w=800&q=80',
  },
  {
    id: 'blog-fan-wars',
    title: 'Fan Wars Go Global: Lakers vs Celtics Breaks Records',
    excerpt: 'Over 40,000 votes in 24 hours as UNTOLD\'s fan community battles across basketball, football, F1, and cricket.',
    date: '2026-03-05',
    category: 'Community',
    image: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&q=80',
  },
];

export default function Blog() {
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
