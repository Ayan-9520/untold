import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import StreamPlayer from '../components/StreamPlayer';
import { contentApi } from '../../api/content';

export default function PlayerScreen() {
  const { id } = useParams();
  const [content, setContent] = useState(null);

  useEffect(() => {
    contentApi.getDocumentaryById(id).then(({ data }) => setContent(data));
  }, [id]);

  if (!content) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center mx-auto max-w-[430px]">
        <div className="w-8 h-8 border-2 border-untold-gold border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return <StreamPlayer content={content} />;
}
