import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';
import { api } from '../api/client';

const FALLBACK_SPORTS = [
  { slug: 'cricket', name: 'Cricket' },
  { slug: 'football', name: 'Football' },
  { slug: 'basketball', name: 'Basketball' },
  { slug: 'tennis', name: 'Tennis' },
  { slug: 'boxing', name: 'Boxing' },
  { slug: 'hockey', name: 'Hockey' },
  { slug: 'formula-1', name: 'Formula 1' },
  { slug: 'olympics', name: 'Olympics' },
];

export default function Hub() {
  const [sports, setSports] = useState(FALLBACK_SPORTS);
  const [images, setImages] = useState({});

  useEffect(() => {
    api.categories.list()
      .then((cats) => {
        if (cats?.length) {
          setSports(cats.map((c) => ({ slug: c.slug, name: c.name })));
        }
      })
      .catch(() => setSports(FALLBACK_SPORTS));
  }, []);

  useEffect(() => {
    api.videos.list({ page_size: 20 })
      .then(({ items }) => {
        const map = {};
        items.forEach((v) => {
          const key = v.category?.slug || v.category?.name?.toLowerCase();
          if (key && v.image_url && !map[key]) map[key] = v.image_url;
        });
        setImages(map);
      })
      .catch(() => {});
  }, []);

  return (
    <>
      <SEO
        title="Sports Hub"
        description="Browse UNTOLD by sport — documentaries, biopics, legends, rivalries, and shorts."
        path="/hub"
      />

      <section className="pt-32 pb-16 sm:pt-40 sm:pb-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <p className="dark:text-untold-gold light:text-untold-gold-dark text-sm font-semibold tracking-[0.3em] uppercase mb-3">
              Browse by Sport
            </p>
            <h1 className="font-display text-4xl sm:text-5xl font-bold dark:text-untold-white light:text-black">
              Sports Hub
            </h1>
            <p className="mt-4 mx-auto max-w-xl text-base dark:text-untold-muted light:text-gray-600">
              Documentaries, biopics, legends, and rivalries — organized sport by sport.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {sports.map((sport) => (
              <Link
                key={sport.slug}
                to={`/explore?sport=${encodeURIComponent(sport.name)}`}
                className="group relative aspect-[4/3] overflow-hidden rounded-xl card-hover"
              >
                <img
                  src={images[sport.slug] || images[sport.name?.toLowerCase()] || `https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=600&q=80`}
                  alt={sport.name}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
                <span className="absolute bottom-3 left-3 right-3 font-display text-lg sm:text-xl font-bold text-white">
                  {sport.name}
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
