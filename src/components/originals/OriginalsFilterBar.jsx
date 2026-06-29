import ContentFilterBar from '../ui/ContentFilterBar';
import {
  ORIGINAL_SPORTS,
  ORIGINAL_FORMATS,
  ORIGINAL_SPORTS_COMING_SOON,
} from '../../data/originalsCatalog';

export default function OriginalsFilterBar({
  activeSport,
  activeFormat,
  onSportChange,
  onFormatChange,
  resultCount,
  isComingSoon,
  sportCounts = {},
  onClear,
}) {
  const sportOptions = ORIGINAL_SPORTS.map((sport) => ({
    value: sport,
    label: sport,
    count: sport !== 'All' ? sportCounts[sport] : undefined,
    badge: ORIGINAL_SPORTS_COMING_SOON.includes(sport) ? 'Soon' : undefined,
    dashed: ORIGINAL_SPORTS_COMING_SOON.includes(sport),
  }));

  const formatOptions = ORIGINAL_FORMATS.map((fmt) => ({ value: fmt, label: fmt }));

  return (
    <ContentFilterBar
      primary={{
        label: 'Sport',
        options: sportOptions,
        active: activeSport,
        onChange: onSportChange,
      }}
      secondary={!isComingSoon ? {
        label: 'Format',
        options: formatOptions,
        active: activeFormat,
        onChange: onFormatChange,
        ariaLabel: 'Filter by format',
      } : undefined}
      resultCount={!isComingSoon ? resultCount : undefined}
      resultLabel="titles"
      onClear={onClear}
      footer={isComingSoon ? `${activeSport} originals — coming soon` : undefined}
    />
  );
}
