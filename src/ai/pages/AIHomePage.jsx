import { Link } from 'react-router-dom';
import { PRODUCTS } from '../../config/ecosystem';
import EcosystemOverview from '../../components/ecosystem/EcosystemOverview';
import Logo from '../../components/brand/Logo';

export default function AIHomePage() {
  const product = PRODUCTS.AI;

  return (
    <div className="min-h-screen dark:bg-untold-dark light:bg-gray-50">
      <header className="border-b dark:border-white/10 light:border-gray-200">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Logo variant="nav" />
            <span className="text-xs font-bold uppercase tracking-[0.2em] text-purple-400">AI</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <Link to="/" className="dark:text-untold-muted light:text-gray-500 hover:text-untold-gold transition-colors">
              UNTOLD ORIGINALS →
            </Link>
            <span className="px-3 py-1.5 rounded-lg bg-purple-500/15 text-purple-300 text-xs font-semibold">
              Phase 2 · Coming soon
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 sm:px-6 py-12 sm:py-16 space-y-16">
        <section className="text-center max-w-3xl mx-auto">
          <p className="text-xs font-bold uppercase tracking-[0.35em] text-purple-400 mb-4">{product.name}</p>
          <h1 className="font-display text-4xl sm:text-5xl font-bold dark:text-white light:text-black leading-tight">
            The AI workflow we use inside{' '}
            <span className="text-gold-gradient">UNTOLD STUDIO</span>
            — built for creators.
          </h1>
          <p className="mt-6 text-lg dark:text-untold-muted light:text-gray-600 leading-relaxed">
            {product.description} Proven on our own documentaries first, then offered to YouTubers,
            agencies, universities, and production houses.
          </p>
        </section>

        <EcosystemOverview variant="ai" showLinks showPlans />
      </main>
    </div>
  );
}
