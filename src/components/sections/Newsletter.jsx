import { useState } from 'react';

export default function Newsletter() {
  const [email, setEmail] = useState('');
  const [done, setDone] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    setDone(true);
    setEmail('');
  };

  return (
    <section className="py-16 sm:py-20 border-t dark:border-untold-border light:border-untold-border-light" aria-labelledby="newsletter-heading">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 text-center">
        <p className="dark:text-untold-gold light:text-untold-gold-dark text-sm font-semibold tracking-[0.3em] uppercase mb-3">
          Stay in the Story
        </p>
        <h2 id="newsletter-heading" className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
          Never Miss a Glory
        </h2>
        <p className="mt-4 text-base dark:text-untold-muted light:text-gray-600 max-w-lg mx-auto">
          New documentaries, biopics, and exclusive UNTOLD drops — straight to your inbox.
        </p>
        {done ? (
          <p className="mt-8 text-untold-gold font-medium animate-fade-in">You&apos;re on the list. Welcome to UNTOLD.</p>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              aria-label="Email address"
              className="flex-1 rounded-lg px-4 py-3 text-sm border
                dark:bg-untold-dark dark:text-untold-white dark:border-untold-border
                light:bg-white light:text-black light:border-gray-300
                focus:outline-none focus:ring-2 focus:ring-untold-gold"
            />
            <button
              type="submit"
              className="rounded-lg bg-untold-gold px-6 py-3 text-sm font-semibold text-untold-dark hover:bg-untold-gold-light transition-colors shrink-0"
            >
              Subscribe
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
