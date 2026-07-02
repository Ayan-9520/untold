"""Default OTT platform pages, FAQ, and promo codes (seeded on first access)."""

PLATFORM_PAGES = [
    {
        "slug": "privacy",
        "category": "legal",
        "title": "Privacy Policy",
        "content_md": """# Privacy Policy

**Effective date:** 1 July 2026

UNTOLD Media Pvt. Ltd. ("UNTOLD", "we", "us") operates the UNTOLD ORIGINALS streaming platform.

## Information we collect
- Account details (name, email, password hash)
- Viewing history, watchlist, and device identifiers
- Payment metadata processed by Stripe or Razorpay (we do not store full card numbers)
- Analytics events to improve recommendations

## How we use data
- Deliver streaming services and membership features
- Personalize content rows and continue-watching
- Send service emails (receipts, live event reminders when opted in)
- Comply with Indian IT Rules and applicable privacy laws

## Your rights
You may request access, correction, or deletion via our Grievance Officer or in-app privacy request tools.

## Contact
Grievance Officer: Rajesh Mehta — grievance@untold.com
""",
    },
    {
        "slug": "terms",
        "category": "legal",
        "title": "Terms of Service",
        "content_md": """# Terms of Service

By using UNTOLD ORIGINALS you agree to these terms.

## Membership
- Plans renew monthly unless cancelled before the renewal date
- VIP includes live sports features where available
- Sharing account credentials beyond your plan device limit is prohibited

## Content
All documentaries, shorts, and magazine content are licensed for personal, non-commercial streaming only.

## Termination
We may suspend accounts that violate these terms or applicable law.

## Governing law
Laws of India; courts at Mumbai shall have jurisdiction.
""",
    },
    {
        "slug": "refund",
        "category": "legal",
        "title": "Refund Policy",
        "content_md": """# Refund Policy

- **Free trial:** Cancel before trial ends to avoid charges
- **Monthly plans:** Refunds within 7 days of first purchase if no significant viewing occurred
- **Annual plans:** Pro-rated refunds at our discretion for technical outages exceeding 24 hours
- **Live events:** No refunds after event start unless the stream failed on our side

Contact support@untold.com with your payment ID for refund requests.
""",
    },
    {
        "slug": "content-guidelines",
        "category": "legal",
        "title": "Content Guidelines",
        "content_md": """# Content Guidelines

UNTOLD ORIGINALS publishes premium sports documentaries and related storytelling.

## Standards
- Fact-checked narratives with clear distinction between commentary and reporting
- Age ratings displayed on all titles (U, U/A 13+, A)
- No glorification of violence or hate speech

## User-generated community features (Fan Wars, Predictions) must not include harassment or illegal content.
""",
    },
    {
        "slug": "app-download",
        "category": "app",
        "title": "Download the UNTOLD App",
        "content_md": """# Watch anywhere

Stream UNTOLD ORIGINALS on mobile with offline downloads (Premium/VIP), push alerts for live events, and continue watching across devices.

## Links
- **iOS:** App Store (coming soon)
- **Android:** Google Play (coming soon)
- **Mobile web:** Add to Home Screen from /app
""",
    },
]

FAQ_ITEMS = [
    {"id": "what-is-untold", "category": "General", "question": "What is UNTOLD ORIGINALS?", "answer": "A premium sports documentary OTT platform — biopics, rivalries, legends, live events, and our quarterly magazine."},
    {"id": "plans", "category": "Membership", "question": "What plans are available?", "answer": "Free (ads + limited catalog), Premium (full originals, HD, ad-free), and VIP (4K, live sports, early access)."},
    {"id": "cancel", "category": "Membership", "question": "How do I cancel?", "answer": "Go to Profile → Billing and click Cancel subscription. Access continues until the end of your billing period."},
    {"id": "devices", "category": "Account", "question": "How many devices can I use?", "answer": "Free: 1 device. Premium: 2 streams. VIP: 4 streams. Manage devices from your Profile."},
    {"id": "offline", "category": "Mobile", "question": "Can I download to watch offline?", "answer": "Premium and VIP members can download select titles in the UNTOLD mobile app."},
    {"id": "live", "category": "Live", "question": "How do live events work?", "answer": "VIP members get premium live streams. Set reminders on the Live page — we notify you when coverage starts."},
    {"id": "subtitles", "category": "Playback", "question": "Are subtitles available?", "answer": "Most originals include English subtitles. Hindi and additional languages roll out via our AI localization pipeline."},
    {"id": "coupon", "category": "Membership", "question": "Can I use a promo code?", "answer": "Enter your code on the Membership page before checkout. Valid codes apply instantly at payment."},
]

DEFAULT_PROMO_CODES = [
    {"code": "UNTOLD20", "discount_percent": 20, "plan_slugs": ["premium", "vip"]},
    {"code": "VIP50", "discount_percent": 50, "plan_slugs": ["vip"]},
]
