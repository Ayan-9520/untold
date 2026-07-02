import { useEffect, useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';

export default function OTTPlatformPage() {
  const [tab, setTab] = useState('legal');
  const [pages, setPages] = useState([]);
  const [faq, setFaq] = useState([]);
  const [promos, setPromos] = useState([]);
  const [selectedSlug, setSelectedSlug] = useState('privacy');
  const [editContent, setEditContent] = useState('');
  const [editTitle, setEditTitle] = useState('');
  const [saving, setSaving] = useState(false);
  const [faqForm, setFaqForm] = useState({ faq_key: '', category: 'General', question: '', answer: '' });
  const [promoForm, setPromoForm] = useState({ code: '', discount_percent: 20, plan_slugs: 'premium,vip' });

  const load = () => {
    studioPlatform.listPages().then(setPages).catch(() => setPages([]));
    studioPlatform.listFaq().then(setFaq).catch(() => setFaq([]));
    studioPlatform.listPromoCodes().then(setPromos).catch(() => setPromos([]));
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    const page = pages.find((p) => p.slug === selectedSlug);
    if (page) {
      setEditTitle(page.title);
      setEditContent(page.content_md);
    }
  }, [pages, selectedSlug]);

  const savePage = async () => {
    setSaving(true);
    try {
      await studioPlatform.updatePage(selectedSlug, { title: editTitle, content_md: editContent });
      load();
    } finally {
      setSaving(false);
    }
  };

  const saveFaq = async (e) => {
    e.preventDefault();
    await studioPlatform.upsertFaq(faqForm);
    setFaqForm({ faq_key: '', category: 'General', question: '', answer: '' });
    load();
  };

  const createPromo = async (e) => {
    e.preventDefault();
    await studioPlatform.createPromoCode({
      code: promoForm.code,
      discount_percent: Number(promoForm.discount_percent),
      plan_slugs: promoForm.plan_slugs.split(',').map((s) => s.trim()),
    });
    setPromoForm({ code: '', discount_percent: 20, plan_slugs: 'premium,vip' });
    load();
  };

  return (
    <div className="space-y-6">
      <StudioPageHeader
        title="OTT Platform"
        description="Manage legal pages, help center FAQ, and consumer promo codes for untoldoriginals.blog"
      />

      <div className="flex flex-wrap gap-2">
        {['legal', 'faq', 'promo'].map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${tab === t ? 'bg-untold-gold text-black' : 'dark:bg-white/5 text-untold-muted'}`}
          >
            {t === 'promo' ? 'Promo codes' : t}
          </button>
        ))}
      </div>

      {tab === 'legal' && (
        <div className="grid lg:grid-cols-4 gap-4">
          <div className="space-y-1">
            {pages.map((p) => (
              <button
                key={p.slug}
                type="button"
                onClick={() => setSelectedSlug(p.slug)}
                className={`w-full text-left px-3 py-2 rounded text-sm ${selectedSlug === p.slug ? 'bg-untold-gold/20 text-untold-gold' : 'dark:text-untold-muted'}`}
              >
                {p.title}
              </button>
            ))}
          </div>
          <div className="lg:col-span-3 space-y-3">
            <input
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="w-full rounded-lg px-3 py-2 dark:bg-untold-surface border dark:border-untold-border text-sm"
            />
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={18}
              className="w-full rounded-lg px-3 py-2 dark:bg-untold-surface border dark:border-untold-border text-sm font-mono"
            />
            <button type="button" onClick={savePage} disabled={saving} className="px-4 py-2 rounded-lg bg-untold-gold text-black text-sm font-semibold">
              {saving ? 'Saving…' : 'Save page'}
            </button>
          </div>
        </div>
      )}

      {tab === 'faq' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <form onSubmit={saveFaq} className="space-y-3 dark:bg-untold-surface p-4 rounded-xl border dark:border-untold-border">
            <h3 className="font-semibold text-white">Add / update FAQ</h3>
            <input placeholder="faq_key" value={faqForm.faq_key} onChange={(e) => setFaqForm({ ...faqForm, faq_key: e.target.value })} className="w-full rounded px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" required />
            <input placeholder="Category" value={faqForm.category} onChange={(e) => setFaqForm({ ...faqForm, category: e.target.value })} className="w-full rounded px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" />
            <input placeholder="Question" value={faqForm.question} onChange={(e) => setFaqForm({ ...faqForm, question: e.target.value })} className="w-full rounded px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" required />
            <textarea placeholder="Answer" value={faqForm.answer} onChange={(e) => setFaqForm({ ...faqForm, answer: e.target.value })} rows={4} className="w-full rounded px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" required />
            <button type="submit" className="px-4 py-2 rounded-lg bg-untold-gold text-black text-sm font-semibold">Save FAQ</button>
          </form>
          <ul className="space-y-2">
            {faq.map((item) => (
              <li key={item.id} className="p-3 rounded-lg border dark:border-untold-border">
                <p className="text-xs text-untold-gold">{item.category}</p>
                <p className="text-sm font-medium text-white">{item.question}</p>
                <p className="text-xs text-untold-muted mt-1">{item.answer}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === 'promo' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <form onSubmit={createPromo} className="space-y-3 dark:bg-untold-surface p-4 rounded-xl border dark:border-untold-border">
            <h3 className="font-semibold text-white">Create promo code</h3>
            <input placeholder="CODE" value={promoForm.code} onChange={(e) => setPromoForm({ ...promoForm, code: e.target.value.toUpperCase() })} className="w-full rounded px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" required />
            <input type="number" min={1} max={100} value={promoForm.discount_percent} onChange={(e) => setPromoForm({ ...promoForm, discount_percent: e.target.value })} className="w-full rounded px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" />
            <input placeholder="Plans: premium,vip" value={promoForm.plan_slugs} onChange={(e) => setPromoForm({ ...promoForm, plan_slugs: e.target.value })} className="w-full rounded px-3 py-2 text-sm dark:bg-black/30 border dark:border-untold-border" />
            <button type="submit" className="px-4 py-2 rounded-lg bg-untold-gold text-black text-sm font-semibold">Create</button>
          </form>
          <ul className="space-y-2">
            {promos.map((p) => (
              <li key={p.code} className="p-3 rounded-lg border dark:border-untold-border flex justify-between">
                <span className="font-mono text-untold-gold">{p.code}</span>
                <span className="text-sm text-untold-muted">{p.discount_percent}% off · {p.plan_slugs?.join(', ')}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
