import { useRef } from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '../icons';

export default function ContentRow({ children, className = '' }) {
  const scrollRef = useRef(null);

  const scroll = (direction) => {
    if (!scrollRef.current) return;
    const amount = scrollRef.current.clientWidth * 0.75;
    scrollRef.current.scrollBy({
      left: direction === 'left' ? -amount : amount,
      behavior: 'smooth',
    });
  };

  return (
    <div className={`relative group/row ${className}`}>
      <button
        onClick={() => scroll('left')}
        aria-label="Scroll left"
        className="absolute left-2 top-1/2 -translate-y-1/2 z-10 hidden md:flex
          h-10 w-10 items-center justify-center rounded-full
          dark:bg-untold-dark/90 light:bg-white/90 shadow-lg
          opacity-0 group-hover/row:opacity-100 transition-opacity duration-300
          hover:bg-untold-gold hover:text-untold-dark
          focus:outline-none focus-visible:opacity-100"
      >
        <ChevronLeftIcon />
      </button>

      <div
        ref={scrollRef}
        className="flex gap-4 overflow-x-auto scrollbar-hide px-4 sm:px-6 lg:px-8 pb-2"
      >
        {children}
      </div>

      <button
        onClick={() => scroll('right')}
        aria-label="Scroll right"
        className="absolute right-2 top-1/2 -translate-y-1/2 z-10 hidden md:flex
          h-10 w-10 items-center justify-center rounded-full
          dark:bg-untold-dark/90 light:bg-white/90 shadow-lg
          opacity-0 group-hover/row:opacity-100 transition-opacity duration-300
          hover:bg-untold-gold hover:text-untold-dark
          focus:outline-none focus-visible:opacity-100"
      >
        <ChevronRightIcon />
      </button>
    </div>
  );
}
