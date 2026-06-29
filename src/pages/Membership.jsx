import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import { PlayIcon } from '../components/icons';
import { useLocale } from '../context/LocaleContext';
import { useWebAuth } from '../context/WebAuthContext';
import membershipApi from '../api/membership';

export default function Membership() {
  const { t } = useTranslation();
  const { currency, region, paymentMethods } = useLocale();
  const { user } = useWebAuth();
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [providers, setProviders] = useState(['stripe']);
  const [loading, setLoading] = useState(true);
  const [checkoutPlan, setCheckoutPlan] = useState(null);

  useEffect(() => {
    membershipApi
      .getPlans(currency, region?.id || region || 'usa')
      .then((data) => {
        setPlans(data.plans || []);
        setProviders(data.payment_providers || ['stripe']);
      })
      .catch(() => {
        setPlans([]);
      })
      .finally(() => setLoading(false));
  }, [currency, region]);

  const handleSubscribe = async (plan) => {
    if (!user) {
      navigate('/login', { state: { from: '/membership' } });
      return;
    }
    if (plan.slug === 'free') {
      await membershipApi.subscribe({
        planSlug: 'free',
        currency,
        region: region?.id || 'usa',
        provider: 'stripe',
      });
      alert('Free plan activated!');
      return;
    }

    setCheckoutPlan(plan.slug);
    const provider = currency === 'INR' ? 'razorpay' : 'stripe';
    try {
      const order = await membershipApi.createOrder({
        planSlug: plan.slug,
        currency,
        region: region?.id || 'usa',
        provider,
      });

      if (provider === 'razorpay' && order.razorpay_order_id) {
        await handleRazorpayCheckout(order, plan);
      } else {
        await membershipApi.verifyPayment({
          provider,
          paymentId: order.payment_id,
          orderId: order.order_id,
          paymentExternalId: order.order_id,
        });
        alert(`Welcome to UNTOLD ${plan.name}!`);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Checkout failed. Try again.');
    } finally {
      setCheckoutPlan(null);
    }
  };

  const handleRazorpayCheckout = (order, plan) =>
    new Promise((resolve, reject) => {
      const loadScript = () =>
        new Promise((res, rej) => {
          if (window.Razorpay) return res();
          const s = document.createElement('script');
          s.src = 'https://checkout.razorpay.com/v1/checkout.js';
          s.onload = res;
          s.onerror = rej;
          document.body.appendChild(s);
        });

      loadScript()
        .then(() => {
          const rzp = new window.Razorpay({
            key: order.razorpay_key_id || 'rzp_test',
            amount: Math.round(order.amount * 100),
            currency: order.currency,
            name: 'UNTOLD',
            description: `${plan.name} Membership`,
            order_id: order.razorpay_order_id,
            handler: async (response) => {
              try {
                await membershipApi.verifyPayment({
                  provider: 'razorpay',
                  paymentId: order.payment_id,
                  orderId: response.razorpay_order_id,
                  paymentExternalId: response.razorpay_payment_id,
                  signature: response.razorpay_signature,
                });
                alert(`Welcome to UNTOLD ${plan.name}!`);
                resolve();
              } catch (e) {
                reject(e);
              }
            },
          });
          rzp.open();
        })
        .catch(reject);
    });

  const displayPlans =
    plans.length > 0
      ? plans.map((p) => ({
          id: p.slug,
          name: p.name,
          price: `${currency === 'INR' || currency === 'RUB' ? Math.round(p.price) : p.price.toFixed(2)}`,
          period: p.slug === 'free' ? t('membership.forever') : t('membership.perMonth'),
          features: p.features,
          cta: p.slug === 'free' ? t('membership.currentPlan') : t(`membership.${p.slug === 'vip' ? 'getVip' : 'startTrial'}`),
          highlight: p.highlight || p.slug === 'premium',
        }))
      : [
          { id: 'free', name: t('membership.free'), price: '0', period: t('membership.forever'), features: t('membership.freeFeatures', { returnObjects: true }), cta: t('membership.currentPlan'), highlight: false },
          { id: 'premium', name: t('membership.premium'), price: '—', period: t('membership.perMonth'), features: t('membership.premiumFeatures', { returnObjects: true }), cta: t('membership.startTrial'), highlight: true },
          { id: 'vip', name: t('membership.vip'), price: '—', period: t('membership.perMonth'), features: t('membership.vipFeatures', { returnObjects: true }), cta: t('membership.getVip'), highlight: false },
        ];

  return (
    <>
      <SEO title="Membership" description="UNTOLD Premium — unlimited sports documentaries and exclusive originals." path="/membership" />

      <section className="pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <p className="dark:text-untold-gold light:text-untold-gold-dark text-sm font-semibold tracking-[0.3em] uppercase mb-3">
              {t('nav.membership')}
            </p>
            <h1 className="font-display text-4xl sm:text-5xl font-bold dark:text-untold-white light:text-black">
              {t('membership.title')}
            </h1>
            <p className="mt-4 mx-auto max-w-xl text-base dark:text-untold-muted light:text-gray-600">
              {t('membership.subtitle')}
            </p>
            <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-500">
              {t('membership.pricedIn', { currency })}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
            {displayPlans.map((plan) => (
              <div
                key={plan.id}
                className={`rounded-2xl p-6 sm:p-8 border transition-all duration-300 card-hover
                  ${plan.highlight
                    ? 'dark:bg-untold-surface light:bg-white border-untold-gold shadow-lg dark:shadow-untold-gold/10 scale-[1.02]'
                    : 'dark:bg-untold-surface/50 light:bg-gray-50 dark:border-untold-border light:border-gray-200'
                  }`}
              >
                {plan.highlight && (
                  <span className="text-[10px] font-bold uppercase tracking-widest text-untold-gold mb-3 block">
                    {t('membership.mostPopular')}
                  </span>
                )}
                <h2 className="font-display text-xl font-bold dark:text-untold-white light:text-black">{plan.name}</h2>
                <p className="mt-3">
                  <span className="text-3xl font-bold dark:text-untold-white light:text-black">{plan.price}</span>
                  <span className="text-sm dark:text-untold-muted light:text-gray-500 ml-1">{plan.period}</span>
                </p>
                <ul className="mt-6 space-y-3">
                  {Array.isArray(plan.features) && plan.features.map((f) => (
                    <li key={f} className="text-sm dark:text-untold-muted light:text-gray-600 flex gap-2">
                      <span className="text-untold-gold">✓</span> {f}
                    </li>
                  ))}
                </ul>
                <Button
                  className="w-full mt-8"
                  variant={plan.highlight ? 'primary' : 'outline'}
                  icon={plan.highlight ? <PlayIcon className="w-4 h-4" /> : undefined}
                  disabled={checkoutPlan === plan.id}
                  onClick={() => handleSubscribe({ slug: plan.id, name: plan.name })}
                >
                  {checkoutPlan === plan.id ? 'Processing…' : plan.cta}
                </Button>
              </div>
            ))}
          </div>

          <div className="mt-10 text-center">
            <p className="text-sm font-semibold dark:text-untold-white light:text-black mb-2">
              {t('membership.paymentMethods')}
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {(providers.length ? providers : paymentMethods).map((method) => (
                <span
                  key={method}
                  className="px-4 py-2 rounded-lg text-sm font-medium dark:bg-white/5 light:bg-gray-100 dark:text-untold-muted light:text-gray-600 border dark:border-untold-border light:border-gray-200 capitalize"
                >
                  {method}
                </span>
              ))}
            </div>
          </div>

          <p className="text-center text-sm dark:text-untold-muted light:text-gray-500 mt-10">
            {t('membership.signIn')}{' '}
            <Link to="/login" className="text-untold-gold hover:underline">{t('membership.signInLink')}</Link>
          </p>
        </div>
      </section>
    </>
  );
}
