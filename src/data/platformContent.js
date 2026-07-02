/** Fallback platform content when API is unavailable */

export const FALLBACK_FAQ = [
  { id: 'what-is-untold', category: 'General', question: 'What is UNTOLD ORIGINALS?', answer: 'A premium sports documentary OTT platform — biopics, rivalries, legends, live events, and our quarterly magazine.' },
  { id: 'plans', category: 'Membership', question: 'What plans are available?', answer: 'Free (ads + limited catalog), Premium (full originals, HD, ad-free), and VIP (4K, live sports, early access).' },
  { id: 'cancel', category: 'Membership', question: 'How do I cancel?', answer: 'Go to Profile → Billing and click Cancel subscription.' },
  { id: 'devices', category: 'Account', question: 'How many devices can I use?', answer: 'Free: 1 device. Premium: 2 streams. VIP: 4 streams.' },
  { id: 'offline', category: 'Mobile', question: 'Can I download offline?', answer: 'Premium and VIP members can download select titles in the mobile app.' },
  { id: 'live', category: 'Live', question: 'How do live events work?', answer: 'VIP members get premium live streams with reminders on the Live page.' },
];

export const FALLBACK_PAGES = {
  privacy: { title: 'Privacy Policy', content_md: '# Privacy Policy\n\nUNTOLD Media Pvt. Ltd. respects your privacy. Contact grievance@untold.com for data requests.' },
  terms: { title: 'Terms of Service', content_md: '# Terms of Service\n\nPersonal streaming only. Mumbai jurisdiction applies.' },
  refund: { title: 'Refund Policy', content_md: '# Refund Policy\n\nRefunds within 7 days of first purchase if no significant viewing occurred.' },
  'content-guidelines': { title: 'Content Guidelines', content_md: '# Content Guidelines\n\nFact-checked sports storytelling with age ratings on all titles.' },
};
