import { useTranslation } from 'react-i18next';
import CategoryPage from '../components/pages/CategoryPage';

export default function Rivalries() {
  const { t } = useTranslation();
  return (
    <CategoryPage
      category="rivalries"
      title={t('nav.rivalries')}
      tagline={t('categories.rivalries.tagline')}
      description={t('categories.rivalries.description')}
    />
  );
}
