import { useState, useEffect } from 'react';
import CategoryPill from '../components/CategoryPill';
import MobileVideoCard, { MobileVideoCardSkeleton } from '../components/MobileVideoCard';
import { contentApi } from '../../api/content';

const categories = ['All', 'Basketball', 'Football', 'Boxing', 'Tennis', 'Hockey'];

export default function OriginalsScreen() {
  const [documentaries, setDocumentaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState('All');

  useEffect(() => {
    contentApi.getDocumentaries().then(({ data }) => {
      setDocumentaries(data);
      setLoading(false);
    });
  }, []);

  const filtered =
    active === 'All'
      ? documentaries
      : documentaries.filter((d) => d.category === active);

  return (
    <div className="pb-4 animate-fade-in">
      <div className="px-4 pt-3 pb-1">
        <h1 className="text-xl font-display font-bold dark:text-untold-white light:text-black">Originals</h1>
        <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">Premium sports documentaries</p>
      </div>

      <div className="flex gap-2 overflow-x-auto scrollbar-hide px-4 py-2 snap-x snap-mandatory">
        {categories.map((cat) => (
          <CategoryPill
            key={cat}
            label={cat}
            active={active === cat}
            onClick={() => setActive(cat)}
          />
        ))}
      </div>

      <div className="grid grid-cols-2 gap-x-3 gap-y-5 px-4">
        {loading
          ? [...Array(6)].map((_, i) => (
              <div key={i} className="[&>article]:w-full">
                <MobileVideoCardSkeleton />
              </div>
            ))
          : filtered.map((item) => (
              <div key={item.id} className="[&>article]:w-full">
                <MobileVideoCard item={item} />
              </div>
            ))}
      </div>

      {!loading && filtered.length === 0 && (
        <p className="text-center text-sm dark:text-untold-muted light:text-gray-500 py-16">
          No originals in this category.
        </p>
      )}
    </div>
  );
}
