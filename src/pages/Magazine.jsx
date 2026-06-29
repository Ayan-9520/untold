import { Link } from 'react-router-dom';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import MagazineCard from '../components/magazine/MagazineCard';
import Badge from '../components/ui/Badge';
import { getMagazineIssues, getFeaturedIssue, MAGAZINE_BRAND, MAGAZINE_ACCESS } from '../data/magazineCatalog';

export default function Magazine() {
  const featured = getFeaturedIssue();
  const issues = getMagazineIssues();

  return (
    <>
      <SEO
        title="UNTOLD E-Magazine"
        description="UNTOLD E-Magazine — premium sports intelligence publication. AI-powered storytelling, analytics, and design."
        path="/magazine"
      />

      <section className="pt-32 pb-12 sm:pt-40">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <Badge variant="premium" className="mb-4">AI-Powered · E-Magazine</Badge>
            <h1 className="font-display text-4xl sm:text-5xl font-bold dark:text-untold-white light:text-black">
              {MAGAZINE_BRAND.name}
            </h1>
            <p className="mt-2 text-untold-gold text-sm font-semibold tracking-[0.3em] uppercase">
              {MAGAZINE_BRAND.tagline}
            </p>
            <p className="mt-5 text-base dark:text-untold-muted light:text-gray-600 leading-relaxed">
              Premium sports storytelling meets analytics. Four editions a year — researched, written,
              designed, and published by UNTOLD&apos;s Magazine Editor AI Agent. Editor-in-Chief approval only.
            </p>
          </div>

          {featured && (
            <div className="relative rounded-2xl overflow-hidden mb-14 min-h-[320px]">
              <img src={featured.coverImage} alt="" className="absolute inset-0 w-full h-full object-cover" />
              <div className="absolute inset-0 hero-gradient" />
              <div className="relative p-8 sm:p-12 flex flex-col sm:flex-row sm:items-end justify-between gap-6">
                <div>
                  <Badge variant="live" pulse size="sm">Latest Issue</Badge>
                  <p className="text-untold-gold-light text-sm mt-3 uppercase tracking-wider">{featured.quarter} {featured.year} · {featured.theme}</p>
                  <h2 className="font-display text-3xl sm:text-4xl font-bold text-white mt-2">{featured.title}</h2>
                  <p className="text-white/75 mt-2 max-w-lg">{featured.pageCount} pages · PDF · Flipbook · App</p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <Link to={`/magazine/${featured.id}`}>
                    <Button size="lg">Read Issue</Button>
                  </Link>
                  {featured.sample && (
                    <span className="self-center text-sm text-untold-gold font-semibold">Free sample edition</span>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="grid sm:grid-cols-3 gap-4 mb-14">
            {[
              { label: 'Free Sample', desc: 'Read our latest sample issue', link: `/magazine/${issues.find((i) => i.sample)?.id || featured?.id}` },
              { label: 'Single Issue', desc: `₹${MAGAZINE_ACCESS.single.priceINRMin}–₹${MAGAZINE_ACCESS.single.priceINRMax} per edition`, link: '/membership' },
              { label: 'Premium / VIP', desc: 'Included in membership', link: '/membership' },
            ].map((tier) => (
              <Link
                key={tier.label}
                to={tier.link}
                className="rounded-xl p-5 border dark:border-untold-border light:border-gray-200 card-premium dark:bg-untold-surface/50 light:bg-gray-50"
              >
                <h3 className="font-semibold dark:text-untold-white light:text-black">{tier.label}</h3>
                <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">{tier.desc}</p>
              </Link>
            ))}
          </div>

          <h2 className="font-display text-2xl font-bold dark:text-untold-white light:text-black mb-6">All Editions</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5 sm:gap-6">
            {issues.map((issue) => (
              <MagazineCard key={issue.id} issue={issue} />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
