import { useTranslation } from 'react-i18next';
import CategoryPage from '../components/pages/CategoryPage';

export default function Legends() {
  const { t } = useTranslation();
  return (
    <CategoryPage
      category="legends"
      title={t('nav.legends')}
      tagline={t('categories.legends.tagline')}
      description={t('categories.legends.description')}
    />
  );
}
