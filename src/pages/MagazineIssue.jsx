import { useEffect, useState } from 'react';
import { useParams, Link, Navigate, useNavigate } from 'react-router-dom';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import FlipbookViewer from '../components/magazine/FlipbookViewer';
import Loader from '../components/ui/Loader';
import { downloadMagazine } from '../api/streaming';
import { useWebAuth } from '../context/WebAuthContext';
import { MAGAZINE_SECTIONS } from '../data/magazineCatalog';
import magazineApi from '../api/magazine';

export default function MagazineIssue() {
  const { id } = useParams();
  const [issue, setIssue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('read');
  const { user } = useWebAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    magazineApi.getIssue(id)
      .then(({ data }) => setIssue(data))
      .catch(() => setIssue(null))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Loader fullScreen label="Loading issue" />;
  if (!issue) return <Navigate to="/magazine" replace />;

  const sections = issue.sections || [];

  const handleDownload = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    try {
      const data = await downloadMagazine(id);
      if (data.download_url?.startsWith('http')) {
        window.open(data.download_url, '_blank');
      } else {
        alert(`Download ready: ${data.title}`);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Download requires a Premium or VIP subscription.';
      alert(msg);
    }
  };

  return (
    <>
      <SEO title={issue.title} description={`${issue.quarter} ${issue.year} — ${issue.theme}`} path={`/magazine/${issue.id}`} />

      <section className="pt-28 sm:pt-32 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <Link to="/magazine" className="text-sm text-untold-gold hover:underline">← UNTOLD E-Magazine</Link>

          <div className="mt-6 grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1">
              <div className="rounded-xl overflow-hidden border dark:border-untold-border light:border-gray-200 sticky top-28">
                <img src={issue.coverImage} alt={issue.title} className="w-full aspect-[3/4] object-cover" />
                <div className="p-5 dark:bg-untold-surface light:bg-white">
                  <Badge variant="gold" size="sm">{issue.quarter} {issue.year}</Badge>
                  <h1 className="font-display text-2xl font-bold dark:text-untold-white light:text-black mt-2">{issue.title}</h1>
                  <p className="text-sm text-untold-gold mt-1">{issue.theme}</p>
                  <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-3">{issue.pageCount} pages</p>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {issue.access === 'free' && <Badge variant="gold" size="sm">Free</Badge>}
                    {issue.access === 'paid' && <Badge variant="outline" size="sm">₹{issue.priceINR}</Badge>}
                    {issue.access === 'premium' && <Badge variant="premium" size="sm">Premium</Badge>}
                    {issue.access === 'vip' && <Badge variant="premium" size="sm">VIP</Badge>}
                  </div>

                  <div className="mt-5 flex flex-col gap-2">
                    <Button className="w-full" onClick={() => setView('flipbook')}>Open Flipbook</Button>
                    <Button variant="outline" className="w-full" onClick={handleDownload}>Download PDF</Button>
                    <Button variant="ghost" className="w-full" onClick={() => setView('read')}>Read Online</Button>
                  </div>
                </div>
              </div>
            </div>

            <div className="lg:col-span-2">
              <div className="flex gap-2 mb-6">
                {['read', 'flipbook'].map((v) => (
                  <button
                    key={v}
                    type="button"
                    onClick={() => setView(v)}
                    className={`px-4 py-2 rounded-full text-sm font-medium capitalize transition-colors
                      ${view === v ? 'bg-untold-gold text-untold-dark' : 'dark:bg-white/5 light:bg-gray-100 dark:text-untold-muted'}`}
                  >
                    {v}
                  </button>
                ))}
              </div>

              {view === 'flipbook' ? (
                <FlipbookViewer issue={issue} sections={sections} />
              ) : (
                <div className="space-y-8">
                  {sections.length === 0 ? (
                    <p className="dark:text-untold-muted light:text-gray-500">Content generating via Magazine AI Agent…</p>
                  ) : (
                    sections.map((sec) => (
                      <article
                        key={sec.id}
                        className="rounded-xl border dark:border-untold-border light:border-gray-200 overflow-hidden dark:bg-untold-surface/50 light:bg-white"
                      >
                        {sec.image && (
                          <img src={sec.image} alt="" className="w-full aspect-video object-cover" />
                        )}
                        <div className="p-6">
                          <Badge variant="outline" size="sm" className="mb-2">
                            {MAGAZINE_SECTIONS.find((s) => s.id === sec.id)?.label || sec.id}
                          </Badge>
                          <h2 className="font-display text-xl font-bold dark:text-untold-white light:text-black">{sec.title}</h2>
                          <p className="mt-3 text-sm dark:text-untold-muted light:text-gray-600 leading-relaxed">
                            {sec.body || sec.excerpt}
                          </p>
                          {sec.items && (
                            <ul className="mt-3 space-y-1">
                              {sec.items.map((item) => (
                                <li key={item} className="text-sm text-untold-gold">• {item}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </article>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
