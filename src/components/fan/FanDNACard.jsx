import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Badge from '../ui/Badge';
import { communityApi } from '../../api/community';

export default function FanDNACard() {
  const [dna, setDna] = useState(null);

  useEffect(() => {
    communityApi.getFanDNA().then(setDna);
  }, []);

  if (!dna) return null;

  return (
    <div className="rounded-xl border dark:border-untold-gold/20 light:border-untold-gold/30 overflow-hidden dark:bg-untold-surface light:bg-white card-premium">
      <div className="p-5 sm:p-6 border-b dark:border-white/5 light:border-gray-100">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-untold-gold">AI Fan DNA</p>
            <h3 className="font-display text-xl font-bold dark:text-untold-white light:text-black mt-1">
              Your Sports Personality
            </h3>
          </div>
          <Badge variant="premium">{dna.badge}</Badge>
        </div>
      </div>
      <div className="p-5 sm:p-6 grid sm:grid-cols-3 gap-4">
        {[
          { label: 'Passion Level', value: dna.passionLevel },
          { label: 'Debate Index', value: dna.debateIndex },
          { label: 'Loyalty Score', value: dna.loyaltyScore },
        ].map((stat) => (
          <div key={stat.label} className="text-center sm:text-left">
            <p className="text-xs dark:text-untold-muted light:text-gray-500">{stat.label}</p>
            <p className="text-2xl font-bold text-untold-gold tabular-nums">{stat.value}%</p>
            <div className="mt-2 h-1.5 rounded-full dark:bg-white/10 light:bg-gray-200 overflow-hidden">
              <div className="h-full bg-untold-gold rounded-full" style={{ width: `${stat.value}%` }} />
            </div>
          </div>
        ))}
      </div>
      <div className="px-5 sm:px-6 pb-5 sm:pb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <p className="text-sm dark:text-untold-muted light:text-gray-500">AI Sports Twin</p>
          <p className="font-semibold dark:text-untold-white light:text-black">
            You think like <span className="text-untold-gold">{dna.sportsTwin}</span>
            <span className="text-xs ml-2 opacity-70">({dna.sportsTwinMatch}% match)</span>
          </p>
        </div>
        <Link to="/profile" className="text-sm font-semibold text-untold-gold hover:underline shrink-0">
          View full DNA →
        </Link>
      </div>
    </div>
  );
}
