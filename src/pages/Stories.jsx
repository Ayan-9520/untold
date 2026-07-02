import { useTranslation } from 'react-i18next';
import CategoryPage from '../components/pages/CategoryPage';

export default function Stories() {
  const { t } = useTranslation();
  return (
    <CategoryPage
      category="stories"
      title={t('nav.stories')}
      tagline={t('categories.stories.tagline')}
      description={t('categories.stories.description')}
    />
  );
}
