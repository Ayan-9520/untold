import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ReelsFeed from '../components/ReelsFeed';
import { contentApi } from '../../api/content';

export default function ShortsScreen() {
  const { state } = useLocation();
  const [shorts, setShorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const startIndex = state?.startIndex ?? 0;

  useEffect(() => {
    contentApi.getShorts().then(({ data }) => {
      setShorts(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="h-dvh bg-black flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-untold-gold border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return <ReelsFeed shorts={shorts} showHeader={false} initialIndex={startIndex} />;
}
