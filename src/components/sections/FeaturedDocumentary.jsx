import { useState, useEffect } from 'react';
import { contentApi } from '../../api/content';
import SectionHeader from '../ui/SectionHeader';
import Button from '../ui/Button';
import { PlayIcon, ClockIcon, StarIcon } from '../icons';

export default function FeaturedDocumentary() {
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    contentApi.getFeatured().then(({ data }) => {
      setDoc(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <section className="py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="h-8 w-48 rounded skeleton mb-8" />
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <div className="aspect-video rounded-xl skeleton" />
            <div className="space-y-4">
              <div className="h-10 w-3/4 rounded skeleton" />
              <div className="h-4 w-full rounded skeleton" />
              <div className="h-4 w-2/3 rounded skeleton" />
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (!doc) return null;

  return (
    <section className="py-16 sm:py-20" aria-labelledby="featured-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader title="Featured Documentary" subtitle="This week's must-watch" />

        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          <div className="relative group overflow-hidden rounded-xl animate-scale-in">
            <img
              src={doc.image}
              alt={doc.title}
              className="w-full aspect-video object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-untold-gold text-untold-dark shadow-2xl">
                <PlayIcon className="w-7 h-7 ml-1" />
              </div>
            </div>
            <span className="absolute top-4 left-4 rounded-full bg-untold-gold px-3 py-1 text-xs font-bold text-untold-dark uppercase tracking-wider">
              Featured
            </span>
          </div>

          <div className="animate-slide-up">
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <span className="rounded-full dark:bg-untold-gold/10 light:bg-untold-gold/20 px-3 py-1 text-xs font-medium dark:text-untold-gold light:text-untold-gold-dark">
                {doc.category}
              </span>
              <span className="flex items-center gap-1 text-sm dark:text-untold-muted light:text-gray-500">
                <ClockIcon />
                {doc.duration}
              </span>
              <span className="text-sm dark:text-untold-muted light:text-gray-500">{doc.year}</span>
              <span className="rounded border dark:border-untold-border light:border-gray-300 px-2 py-0.5 text-xs dark:text-untold-muted light:text-gray-500">
                {doc.rating}
              </span>
            </div>

            <h2 id="featured-heading" className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black leading-tight">
              {doc.title}
            </h2>

            <p className="mt-4 text-base dark:text-untold-muted light:text-gray-600 leading-relaxed">
              {doc.description}
            </p>

            <div className="mt-6 flex items-center gap-2">
              <div className="flex text-untold-gold">
                {[...Array(5)].map((_, i) => (
                  <StarIcon key={i} className="w-4 h-4" />
                ))}
              </div>
              <span className="text-sm dark:text-untold-muted light:text-gray-500">Critics' Choice</span>
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button size="lg" icon={<PlayIcon />}>
                Watch Now
              </Button>
              <Button variant="outline" size="lg">
                Add to List
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
