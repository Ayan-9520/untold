import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import SEO from '../components/SEO';
import MarkdownContent from '../components/ui/MarkdownContent';
import platformApi from '../api/platform';
import { FALLBACK_PAGES } from '../data/platformContent';

const SLUG_META = {
  privacy: { title: 'Privacy Policy', description: 'How UNTOLD ORIGINALS handles your data.' },
  terms: { title: 'Terms of Service', description: 'Terms for using UNTOLD ORIGINALS.' },
  refund: { title: 'Refund Policy', description: 'Membership refund policy.' },
  'content-guidelines': { title: 'Content Guidelines', description: 'Editorial and community standards.' },
};

export default function LegalPage() {
  const { slug } = useParams();
  const meta = SLUG_META[slug] || { title: 'Legal', description: 'UNTOLD legal information' };
  const [page, setPage] = useState(FALLBACK_PAGES[slug] || null);

  useEffect(() => {
    platformApi.getPage(slug).then(setPage).catch(() => {
      setPage(FALLBACK_PAGES[slug] || { title: meta.title, content_md: `# ${meta.title}\n\nContent coming soon.` });
    });
  }, [slug, meta.title]);

  if (!page) return null;

  return (
    <>
      <SEO title={page.title || meta.title} description={meta.description} path={`/legal/${slug}`} />
      <section className="pt-28 pb-16">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <MarkdownContent content={page.content_md} />
        </div>
      </section>
    </>
  );
}
