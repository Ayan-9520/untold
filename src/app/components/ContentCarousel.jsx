import { useRef } from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '../../components/icons';

export default function ContentCarousel({ title, subtitle, children }) {
  const scrollRef = useRef(null);

  const scroll = (dir) => {
    scrollRef.current?.scrollBy({
      left: dir === 'left' ? -200 : 200,
      behavior: 'smooth',
    });
  };

  return (
    <section className="mb-6">
      <div className="flex items-end justify-between px-4 mb-3">
        <div>
          <h2 className="text-sm font-semibold dark:text-untold-white light:text-black">
            {title}
          </h2>
          {subtitle && (
            <p className="text-[11px] dark:text-untold-muted light:text-gray-400 mt-0.5">
              {subtitle}
            </p>
          )}
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => scroll('left')}
            className="p-1 rounded-full dark:bg-white/5 light:bg-black/5 active:scale-90 transition-transform"
            aria-label="Scroll left"
          >
            <ChevronLeftIcon className="w-4 h-4 dark:text-untold-muted light:text-gray-400" />
          </button>
          <button
            onClick={() => scroll('right')}
            className="p-1 rounded-full dark:bg-white/5 light:bg-black/5 active:scale-90 transition-transform"
            aria-label="Scroll right"
          >
            <ChevronRightIcon className="w-4 h-4 dark:text-untold-muted light:text-gray-400" />
          </button>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex gap-2.5 overflow-x-auto scrollbar-hide px-4 pb-1 snap-x snap-mandatory"
      >
        {children}
      </div>
    </section>
  );
}
