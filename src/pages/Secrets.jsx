import { useTranslation } from 'react-i18next';
import CategoryPage from '../components/pages/CategoryPage';

export default function Secrets() {
  const { t } = useTranslation();
  return (
    <CategoryPage
      category="secrets"
      title={t('nav.secrets')}
      tagline={t('categories.secrets.tagline')}
      description={t('categories.secrets.description')}
    />
  );
}
