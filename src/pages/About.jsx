import SEO from '../components/SEO';
import Button from '../components/ui/Button';
import { PlayIcon } from '../components/icons';

const stats = [
  { value: '50+', label: 'Documentaries' },
  { value: '12M+', label: 'Viewers Worldwide' },
  { value: '15', label: 'Sports Covered' },
  { value: '8', label: 'Award Wins' },
];

const values = [
  {
    title: 'Authentic Storytelling',
    description: 'We go beyond the headlines to uncover the raw, human stories that define athletic greatness.',
  },
  {
    title: 'Unfiltered Truth',
    description: 'No sugarcoating. We present the triumphs, scandals, and redemption arcs as they happened.',
  },
  {
    title: 'Cinematic Quality',
    description: 'Every frame is crafted with the production value of a feature film, because these stories deserve it.',
  },
];

export default function About() {
  return (
    <>
      <SEO
        title="About"
        description="Learn about UNTOLD — the premium sports documentary platform revealing the stories behind athletic glory."
        path="/about"
      />

      {/* Hero */}
      <section className="relative pt-32 pb-20 sm:pt-40 sm:pb-28 overflow-hidden">
        <div className="absolute inset-0 dark:bg-gradient-to-b dark:from-untold-gold/5 dark:to-transparent light:bg-gradient-to-b light:from-untold-gold/10 light:to-transparent" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <p className="dark:text-untold-gold light:text-untold-gold-dark text-sm font-semibold tracking-[0.3em] uppercase mb-4 animate-fade-in">
            Our Mission
          </p>
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl font-bold dark:text-untold-white light:text-black animate-slide-up">
            Every Legend Has a Story
            <br />
            <span className="text-gold-gradient">Worth Telling</span>
          </h1>
          <p className="mt-6 mx-auto max-w-2xl text-lg dark:text-untold-muted light:text-gray-600 leading-relaxed animate-slide-up stagger-1">
            UNTOLD is a premium storytelling platform for every arena — biopics, documentaries, rivalries,
            and untold stories from football pitches to F1 paddocks, boxing rings to Olympic stadiums.
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-y dark:border-untold-border light:border-untold-border-light">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <div key={stat.label} className={`text-center animate-slide-up stagger-${i + 1}`}>
                <p className="font-display text-3xl sm:text-4xl font-bold text-untold-gold">{stat.value}</p>
                <p className="mt-1 text-sm dark:text-untold-muted light:text-gray-500">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Story */}
      <section className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="relative overflow-hidden rounded-2xl">
              <img
                src="https://images.unsplash.com/photo-1461896836934-ffe607ad7a85?w=800&q=80"
                alt="Behind the scenes of a sports documentary"
                className="w-full aspect-[4/3] object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-tr from-untold-gold/20 to-transparent" />
            </div>
            <div>
              <h2 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
                Born from a Simple Belief
              </h2>
              <p className="mt-4 text-base dark:text-untold-muted light:text-gray-600 leading-relaxed">
                The world sees the glory — the trophies, the records, the celebrations. But behind
                every iconic moment lies a story of sacrifice, controversy, and humanity that rarely
                makes the highlight reel.
              </p>
              <p className="mt-4 text-base dark:text-untold-muted light:text-gray-600 leading-relaxed">
                UNTOLD was created to change that. We partner with award-winning filmmakers to
                produce cinematic documentaries that pull back the curtain on sports history's most
                compelling narratives.
              </p>
              <div className="mt-8">
                <Button size="lg" icon={<PlayIcon />}>
                  Watch Our Reel
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-16 sm:py-24 dark:bg-untold-surface/50 light:bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center dark:text-untold-white light:text-black mb-12">
            What We Stand For
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {values.map((value, i) => (
              <div
                key={value.title}
                className={`p-6 sm:p-8 rounded-xl dark:bg-untold-surface light:bg-white
                  border dark:border-untold-border light:border-untold-border-light
                  card-hover animate-slide-up stagger-${i + 1}`}
              >
                <div className="h-1 w-12 bg-untold-gold rounded-full mb-5" />
                <h3 className="text-xl font-semibold dark:text-untold-white light:text-black">
                  {value.title}
                </h3>
                <p className="mt-3 text-sm dark:text-untold-muted light:text-gray-600 leading-relaxed">
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
