import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import SectionReveal from '../ui/SectionReveal';
import { useEngagement } from '../../context/EngagementContext';
import streamingApi from '../../api/streaming';
import { useEffect, useState } from 'react';

export default function ContinueWatching() {
  const { t } = useTranslation();
  const { continueWatching: localItems } = useEngagement();
  const [apiItems, setApiItems] = useState([]);

  useEffect(() => {
    streamingApi.getContinueWatching(8).then(setApiItems);
  }, []);

  const items = apiItems.length
    ? apiItems.map((item) => ({
        id: item.video_id,
        title: item.title,
        image: item.image_url,
        progress: (item.progress_percent || 0) / 100,
      }))
    : localItems.map((item) => ({
        id: item.id,
        title: item.title,
        image: item.image,
        progress: item.progress,
      }));

  if (!items.length) return null;

  return (
    <SectionReveal className="ott-row" aria-labelledby="continue-watching">
      <SectionHeader
        title={t('home.continueWatching', 'Continue Watching')}
        subtitle={t('home.continueSubtitle', 'Pick up where you left off')}
        viewAllLink="/profile"
      />
      <ContentRow>
        {items.map((item) => (
          <Link
            key={item.id}
            to={`/video/${item.id}`}
            className="ott-continue-card shrink-0 w-[200px] sm:w-[240px] group"
          >
            <div className="relative aspect-video rounded-lg overflow-hidden border border-untold-border/80">
              <img src={item.image} alt="" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/15">
                <div className="h-full bg-untold-gold transition-all" style={{ width: `${Math.min(item.progress * 100, 100)}%` }} />
              </div>
              <span className="absolute bottom-2 left-2 text-[10px] font-bold uppercase tracking-wider text-white/90">
                {t('rows.resume')}
              </span>
            </div>
            <p className="mt-2 text-sm font-semibold dark:text-untold-white light:text-black line-clamp-2 group-hover:text-untold-gold transition-colors">
              {item.title}
            </p>
          </Link>
        ))}
      </ContentRow>
    </SectionReveal>
  );
}
