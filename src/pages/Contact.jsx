import { useState } from 'react';
import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import { MailIcon } from '../components/icons';
import { contentApi } from '../api/content';

export default function Contact() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setStatus({ type: '', message: '' });

    try {
      const { data } = await contentApi.submitContact(form);
      setStatus({ type: 'success', message: data.message });
      setForm({ name: '', email: '', subject: '', message: '' });
    } catch {
      setStatus({ type: 'error', message: 'Something went wrong. Please try again.' });
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass = `w-full rounded-lg px-4 py-3 text-sm transition-colors
    dark:bg-untold-surface dark:text-untold-white dark:border-untold-border
    light:bg-white light:text-black light:border-gray-300
    border focus:outline-none focus:ring-2 focus:ring-untold-gold focus:border-transparent`;

  return (
    <>
      <SEO
        title="Contact"
        description="Get in touch with the UNTOLD team. Partnerships, press inquiries, and general questions welcome."
        path="/contact"
      />

      <section className="pt-32 pb-16 sm:pt-40 sm:pb-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16">
            <div>
              <p className="dark:text-untold-gold light:text-untold-gold-dark text-sm font-semibold tracking-[0.3em] uppercase mb-3">
                Get in Touch
              </p>
              <h1 className="font-display text-4xl sm:text-5xl font-bold dark:text-untold-white light:text-black">
                Let's Talk Stories
              </h1>
              <p className="mt-4 text-base dark:text-untold-muted light:text-gray-600 leading-relaxed max-w-md">
                Whether you're a filmmaker, athlete, brand, or fan — we'd love to hear from you.
              </p>

              <div className="mt-10 space-y-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-lg dark:bg-untold-gold/10 light:bg-untold-gold/15">
                    <MailIcon className="w-5 h-5 dark:text-untold-gold light:text-untold-gold-dark" />
                  </div>
                  <div>
                    <h3 className="font-semibold dark:text-untold-white light:text-black">Email</h3>
                    <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
                      hello@untold.com
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-lg dark:bg-untold-gold/10 light:bg-untold-gold/15">
                    <MailIcon className="w-5 h-5 dark:text-untold-gold light:text-untold-gold-dark" />
                  </div>
                  <div>
                    <h3 className="font-semibold dark:text-untold-white light:text-black">Press</h3>
                    <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
                      press@untold.com
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <form
              onSubmit={handleSubmit}
              className="p-6 sm:p-8 rounded-2xl dark:bg-untold-surface light:bg-gray-50
                border dark:border-untold-border light:border-untold-border-light"
            >
              <div className="space-y-5">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium dark:text-untold-white light:text-black mb-1.5">
                    Name
                  </label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    value={form.name}
                    onChange={handleChange}
                    className={inputClass}
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium dark:text-untold-white light:text-black mb-1.5">
                    Email
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={form.email}
                    onChange={handleChange}
                    className={inputClass}
                    placeholder="you@example.com"
                  />
                </div>
                <div>
                  <label htmlFor="subject" className="block text-sm font-medium dark:text-untold-white light:text-black mb-1.5">
                    Subject
                  </label>
                  <input
                    id="subject"
                    name="subject"
                    type="text"
                    required
                    value={form.subject}
                    onChange={handleChange}
                    className={inputClass}
                    placeholder="What's this about?"
                  />
                </div>
                <div>
                  <label htmlFor="message" className="block text-sm font-medium dark:text-untold-white light:text-black mb-1.5">
                    Message
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={5}
                    value={form.message}
                    onChange={handleChange}
                    className={`${inputClass} resize-none`}
                    placeholder="Tell us your story..."
                  />
                </div>

                {status.message && (
                  <p
                    className={`text-sm ${status.type === 'success' ? 'text-green-500' : 'text-red-500'}`}
                    role="alert"
                  >
                    {status.message}
                  </p>
                )}

                <Button type="submit" size="lg" className="w-full" disabled={submitting}>
                  {submitting ? 'Sending...' : 'Send Message'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </section>
    </>
  );
}
