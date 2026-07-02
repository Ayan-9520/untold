import { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import { PlayIcon } from '../components/icons';
import { useLocale } from '../context/LocaleContext';
import { useWebAuth } from '../context/WebAuthContext';
import membershipApi from '../api/membership';
import platformApi from '../api/platform';
import { buildFallbackPlans, mapApiPlans } from '../utils/planDisplay';
import { formatPrice } from '../data/regionalConfig';

export default function Membership() {
  const { t } = useTranslation();
  const { currency, region, paymentMethods } = useLocale();
  const { user } = useWebAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [plans, setPlans] = useState([]);
  const [providers, setProviders] = useState(['stripe']);
  const [loading, setLoading] = useState(true);
  const [checkoutPlan, setCheckoutPlan] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [promoCode, setPromoCode] = useState('');
  const [promoDiscount, setPromoDiscount] = useState(null);
  const [promoError, setPromoError] = useState('');

  useEffect(() => {
    membershipApi
      .getPlans(currency, region?.id || region || 'usa')
      .then((data) => {
        setPlans(data.plans || []);
        setProviders(data.payment_providers || ['stripe']);
      })
      .catch(() => setPlans([]))
      .finally(() => setLoading(false));
  }, [currency, region]);

  useEffect(() => {
    const paymentStatus = searchParams.get('payment');
    const paymentId = searchParams.get('payment_id');
    if (paymentStatus === 'success' && paymentId && user) {
      membershipApi
        .verifyPayment({ provider: 'stripe', paymentId: Number(paymentId), orderId: paymentId, paymentExternalId: paymentId })
        .then(() => alert('Payment successful! Welcome to UNTOLD Premium.'))
        .catch(() => {});
    }
  }, [searchParams, user]);

  const displayPlans =
    plans.length > 0
      ? mapApiPlans(plans, currency, t)
      : buildFallbackPlans(currency, t);

  const applyPromo = async () => {
    setPromoError('');
    if (!promoCode.trim()) return;
    try {
      const result = await platformApi.validatePromo(promoCode, 'premium');
      setPromoDiscount(result.discount_percent);
    } catch (err) {
      setPromoDiscount(null);
      setPromoError(err.response?.data?.detail || 'Invalid promo code');
    }
  };

  const priceWithPromo = (plan) => {
    let amount = billingCycle === 'annual' ? plan.priceAnnual : plan.priceMonthly;
    if (promoDiscount && plan.slug !== 'free') {
      amount = Math.round(amount * (1 - promoDiscount / 100) * 100) / 100;
    }
    if (plan.slug === 'free') return formatPrice(0, currency);
    return formatPrice(amount, currency);
  };

  const handleSubscribe = async (plan) => {
    if (!user) {
      navigate('/login', { state: { from: '/membership' } });
      return;
    }
    if (plan.slug === 'free' || plan.id === 'free') {
      await membershipApi.subscribe({
        planSlug: 'free',
        currency,
        region: region?.id || 'usa',
        provider: 'stripe',
      });
      alert('Free plan activated!');
      return;
    }

    const slug = plan.slug || plan.id;
    setCheckoutPlan(slug);
    const provider = currency === 'INR' ? 'razorpay' : 'stripe';
    try {
      const order = await membershipApi.createOrder({
        planSlug: slug,
        currency,
        region: region?.id || 'usa',
        provider,
        promoCode: promoDiscount ? promoCode : undefined,
        billingCycle,
      });

      if (provider === 'razorpay' && order.razorpay_order_id) {
        await handleRazorpayCheckout(order, plan);
      } else if (order.checkout_url) {
        window.location.href = order.checkout_url;
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

  return (
    <>
      <SEO title="Membership" description="UNTOLD Premium — unlimited sports documentaries and exclusive originals." path="/membership" />

      <section className="pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
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
              {currency === 'INR'
                ? t('membership.pricedInInr')
                : t('membership.pricedIn', { currency })}
            </p>

            <div className="mt-6 inline-flex rounded-full border dark:border-untold-border light:border-gray-200 p-1">
              {['monthly', 'annual'].map((cycle) => (
                <button
                  key={cycle}
                  type="button"
                  className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition-colors ${
                    billingCycle === cycle ? 'bg-untold-gold text-black' : 'text-untold-muted'
                  }`}
                  onClick={() => setBillingCycle(cycle)}
                >
                  {cycle === 'monthly' ? t('membership.monthly') : t('membership.annual')}
                  {cycle === 'annual' ? ` (${t('membership.annualSave')})` : ''}
                </button>
              ))}
            </div>
          </div>

          <div className="max-w-md mx-auto mb-10 flex gap-2">
            <input
              type="text"
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
              placeholder={t('membership.promoCode')}
              className="flex-1 rounded-lg px-3 py-2 text-sm dark:bg-untold-surface light:bg-white border dark:border-untold-border light:border-gray-200"
            />
            <Button variant="outline" onClick={applyPromo}>{t('membership.apply')}</Button>
          </div>
          {promoDiscount && <p className="text-center text-sm text-untold-gold mb-4">{promoDiscount}% {t('membership.discountApplied')}</p>}
          {promoError && <p className="text-center text-sm text-red-400 mb-4">{promoError}</p>}

          {loading ? (
            <p className="text-center text-untold-muted">{t('common.loading')}</p>
          ) : (
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
                    <span className="text-3xl font-bold dark:text-untold-white light:text-black">
                      {priceWithPromo(plan)}
                    </span>
                    <span className="text-sm dark:text-untold-muted light:text-gray-500 ml-1">
                      {plan.slug === 'free' ? plan.period : billingCycle === 'annual' ? t('membership.perYear') : plan.period}
                    </span>
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
                    onClick={() => handleSubscribe(plan)}
                  >
                    {checkoutPlan === plan.id ? t('common.processing') : plan.cta}
                  </Button>
                </div>
              ))}
            </div>
          )}

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
            {' · '}
            <Link to="/help" className="text-untold-gold hover:underline">{t('membership.helpFaq')}</Link>
          </p>
        </div>
      </section>
    </>
  );
}
