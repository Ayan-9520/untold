import { Link } from 'react-router-dom';
import SEO from '../components/SEO';

const sports = [
  { slug: 'cricket', name: 'Cricket', image: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=600&q=80' },
  { slug: 'football', name: 'Football', image: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=600&q=80' },
  { slug: 'basketball', name: 'Basketball', image: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=600&q=80' },
  { slug: 'tennis', name: 'Tennis', image: 'https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=600&q=80' },
  { slug: 'boxing', name: 'Boxing', image: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=600&q=80' },
  { slug: 'hockey', name: 'Hockey', image: 'https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=600&q=80' },
  { slug: 'formula-1', name: 'Formula 1', image: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=600&q=80' },
  { slug: 'olympics', name: 'Olympics', image: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=600&q=80' },
];

export default function Hub() {
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
                to={`/originals`}
                className="group relative aspect-[4/3] overflow-hidden rounded-xl card-hover"
              >
                <img
                  src={sport.image}
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
