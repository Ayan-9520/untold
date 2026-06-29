import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Logo from '../brand/Logo';
import {
  InstagramIcon,
  XIcon,
  YoutubeIcon,
  LinkedInIcon,
  FacebookIcon,
  MailIcon,
  PhoneIcon,
  MapPinIcon,
} from '../icons';
import { FOOTER_CONTACT, SOCIAL_LINKS } from '../../data/siteConfig';

const ICON_MAP = {
  youtube: YoutubeIcon,
  instagram: InstagramIcon,
  x: XIcon,
  linkedin: LinkedInIcon,
  facebook: FacebookIcon,
};

const navigationKeys = [
  { to: '/', key: 'home' },
  { to: '/originals', key: 'originals' },
  { to: '/shorts', key: 'shorts' },
  { to: '/live', key: 'live' },
  { to: '/news', key: 'news' },
  { to: '/membership', key: 'membership' },
  { to: '/about', key: 'about' },
];

const categoryNavKeys = [
  { to: '/legends', key: 'legends' },
  { to: '/rivalries', key: 'rivalries' },
  { to: '/stories', key: 'stories' },
  { to: '/secrets', key: 'secrets' },
  { to: '/events', key: 'events' },
  { to: '/magazine', key: 'magazine' },
  { to: '/fan-wars', key: 'fanWars' },
];

const supportKeys = [
  { to: '#contact', key: 'contactLink' },
  { to: '/membership', key: 'membership' },
  { to: '/watchlist', key: 'watchlist' },
  { to: '/hub', key: 'hub' },
  { to: '/app', key: 'app' },
];

const legalKeys = [
  { to: '#privacy', key: 'privacy' },
  { to: '#terms', key: 'terms' },
  { to: '#grievance', key: 'grievance' },
];

function FooterLinkGroup({ title, links, t, ns = 'nav' }) {
  const labelFor = (link) => {
    if (link.key === 'contactLink') return t('footer.contactLink');
    if (ns === 'footer') return t(`footer.${link.key}`);
    return t(`nav.${link.key}`);
  };

  return (
    <div className="site-footer-col">
      <h3 className="site-footer-heading">{title}</h3>
      <ul className="site-footer-links">
        {links.map((link) => (
          <li key={link.key}>
            {link.to.startsWith('#') ? (
              <a href={link.to} className="site-footer-link">
                {labelFor(link)}
              </a>
            ) : (
              <Link to={link.to} className="site-footer-link">
                {labelFor(link)}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function Footer() {
  const { t } = useTranslation();
  const mapSrc = `https://maps.google.com/maps?q=${encodeURIComponent(FOOTER_CONTACT.mapQuery)}&t=&z=15&ie=UTF8&iwloc=&output=embed`;

  return (
    <footer id="contact" className="site-footer">
      <div className="site-footer-accent" aria-hidden="true" />

      <div className="site-footer-inner">
        {/* Premium newsletter + membership strip */}
        <section className="site-footer-premium" aria-labelledby="footer-newsletter-title">
          <div className="site-footer-premium-copy">
            <p className="site-footer-eyebrow">{t('footer.newsletterSubtitle')}</p>
            <h2 id="footer-newsletter-title" className="site-footer-premium-title">
              {t('footer.newsletter')}
            </h2>
            <p className="site-footer-premium-desc">{t('brand.description')}</p>
          </div>

          <div className="site-footer-premium-actions">
            <form className="site-footer-newsletter" onSubmit={(e) => e.preventDefault()}>
              <input
                type="email"
                placeholder={t('footer.emailPlaceholder')}
                aria-label="Newsletter email"
                className="site-footer-newsletter-input"
              />
              <button type="submit" className="site-footer-newsletter-btn">
                {t('footer.subscribe')}
              </button>
            </form>
            <Link to="/membership" className="site-footer-membership-btn">
              {t('nav.membership')}
            </Link>
          </div>
        </section>

        {/* Main content */}
        <div className="site-footer-main">
          <div className="site-footer-brand">
            <Link to="/" className="inline-block">
              <Logo variant="horizontal" showTagline />
            </Link>
            <p className="site-footer-tagline">{t('brand.description')}</p>
            <div className="site-footer-social">
              {SOCIAL_LINKS.map(({ label, href, icon }) => {
                const Icon = ICON_MAP[icon];
                return (
                  <a
                    key={label}
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={label}
                    className="site-footer-social-btn"
                  >
                    <Icon className="w-4 h-4 sm:w-[1.125rem] sm:h-[1.125rem]" />
                  </a>
                );
              })}
            </div>
          </div>

          <div className="site-footer-nav-grid">
            <FooterLinkGroup title={t('footer.navigation', 'Navigation')} links={navigationKeys} t={t} />
            <FooterLinkGroup title={t('footer.categories')} links={categoryNavKeys} t={t} />
            <FooterLinkGroup title={t('footer.support', 'Support')} links={supportKeys} t={t} />
            <FooterLinkGroup title={t('footer.legal', 'Legal')} links={legalKeys} t={t} ns="footer" />
          </div>

          <div className="site-footer-contact-card">
            <h3 className="site-footer-heading">{t('footer.contact')}</h3>
            <ul className="site-footer-contact-list">
              <li className="site-footer-contact-item">
                <MapPinIcon className="site-footer-contact-icon" />
                <div className="min-w-0">
                  <p className="site-footer-contact-label">{FOOTER_CONTACT.company}</p>
                  <p className="site-footer-contact-text">{FOOTER_CONTACT.address}</p>
                </div>
              </li>
              <li className="site-footer-contact-item">
                <MailIcon className="site-footer-contact-icon" />
                <a href={`mailto:${FOOTER_CONTACT.email}`} className="site-footer-contact-text site-footer-link">
                  {FOOTER_CONTACT.email}
                </a>
              </li>
              <li className="site-footer-contact-item">
                <PhoneIcon className="site-footer-contact-icon" />
                <a href={`tel:${FOOTER_CONTACT.phone.replace(/\s/g, '')}`} className="site-footer-contact-text site-footer-link">
                  {FOOTER_CONTACT.phone}
                </a>
              </li>
            </ul>

            <div id="grievance" className="site-footer-grievance">
              <h4 className="site-footer-grievance-title">{t('footer.grievance')}</h4>
              <p className="site-footer-contact-label">{FOOTER_CONTACT.grievanceOfficer}</p>
              <a href={`mailto:${FOOTER_CONTACT.grievanceEmail}`} className="site-footer-link site-footer-contact-text">
                {FOOTER_CONTACT.grievanceEmail}
              </a>
              <a href={`tel:${FOOTER_CONTACT.grievancePhone.replace(/\s/g, '')}`} className="site-footer-link site-footer-contact-text block mt-1">
                {FOOTER_CONTACT.grievancePhone}
              </a>
            </div>
          </div>
        </div>

        {/* Map */}
        <div className="site-footer-map">
          <iframe
            title="UNTOLD office location"
            src={mapSrc}
            className="site-footer-map-frame"
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        </div>

        {/* Bottom bar */}
        <div className="site-footer-bottom">
          <p className="site-footer-copyright">
            &copy; {new Date().getFullYear()} UNTOLD Media Pvt. Ltd. {t('footer.rights')}
          </p>
          <nav className="site-footer-legal-nav" aria-label="Legal">
            <a id="privacy" href="#" className="site-footer-bottom-link">{t('footer.privacy')}</a>
            <a id="terms" href="#" className="site-footer-bottom-link">{t('footer.terms')}</a>
            <a href="#contact" className="site-footer-bottom-link">{t('footer.contactLink')}</a>
          </nav>
        </div>
      </div>
    </footer>
  );
}
