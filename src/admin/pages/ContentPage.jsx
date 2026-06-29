import { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import SearchFilter from '../components/SearchFilter';
import Modal from '../components/Modal';
import VideoUploadForm from '../components/VideoUploadForm';
import Chip from '../../components/ui/Chip';
import { videos, categories } from '../api/adminApi';
import { CONTENT_PILLARS } from '../../data/contentPillars';
import { PlusIcon } from '../components/AdminIcons';

export default function ContentPage() {
  const [activePillar, setActivePillar] = useState('originals');
  const [videoList, setVideoList] = useState([]);
  const [categoryList, setCategoryList] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [page, setPage] = useState(1);

  const pillar = CONTENT_PILLARS.find((p) => p.id === activePillar) || CONTENT_PILLARS[0];
  const isCatalogPillar = Boolean(pillar.catalog);

  const fetchContent = () => {
    if (isCatalogPillar) {
      setLoading(false);
      setVideoList([]);
      return;
    }
    setLoading(true);
    Promise.all([
      videos.list({
        page,
        page_size: 20,
        search: search || undefined,
        video_type: pillar.videoType || undefined,
      }),
      categories.list(),
    ])
      .then(([v, c]) => {
        const filtered = pillar.slug
          ? v.items.filter((item) => item.category?.slug === pillar.slug || !item.category)
          : v.items;
        setVideoList(filtered.length ? filtered : v.items);
        setCategoryList(c);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchContent(); }, [page, activePillar]);

  useEffect(() => {
    const timer = setTimeout(() => fetchContent(), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleDelete = async (video) => {
    if (!confirm(`Remove "${video.title}"?`)) return;
    await videos.delete(video.id);
    fetchContent();
  };

  const columns = [
    {
      key: 'title',
      label: 'Video',
      render: (row) => (
        <div className="flex items-center gap-3">
          {row.image_url && (
            <img src={row.image_url} alt="" className="w-12 h-8 rounded object-cover" />
          )}
          <div className="min-w-0">
            <p className="font-medium truncate max-w-[200px]">{row.title}</p>
            <p className="text-xs dark:text-untold-muted light:text-gray-500">{row.category?.name || pillar.label}</p>
          </div>
        </div>
      ),
    },
    { key: 'video_type', label: 'Type', render: (row) => <span className="capitalize text-xs">{row.video_type}</span> },
    { key: 'duration', label: 'Duration' },
    { key: 'rating', label: 'Rating' },
    { key: 'views_count', label: 'Views', render: (row) => row.views_count?.toLocaleString() },
    {
      key: 'flags',
      label: 'Flags',
      render: (row) => (
        <div className="flex gap-1">
          {row.is_featured && <span className="px-1.5 py-0.5 rounded text-[10px] bg-untold-gold/15 text-untold-gold">Featured</span>}
          {row.is_trending && <span className="px-1.5 py-0.5 rounded text-[10px] bg-blue-500/15 text-blue-400">Trending</span>}
        </div>
      ),
    },
    {
      key: 'actions',
      label: '',
      render: (row) => (
        <button onClick={(e) => { e.stopPropagation(); handleDelete(row); }} className="text-xs text-red-400 hover:underline">
          Remove
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Content Management</h1>
          <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
            Manage all UNTOLD content pillars — upload once, AI localizes globally
          </p>
        </div>
        {!isCatalogPillar && (
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-untold-gold text-untold-dark text-sm font-semibold hover:bg-untold-gold-light transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Upload Video
          </button>
        )}
      </div>

      <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
        {CONTENT_PILLARS.map((p) => (
          <Chip key={p.id} active={activePillar === p.id} onClick={() => setActivePillar(p.id)}>
            {p.label}
          </Chip>
        ))}
      </div>

      {isCatalogPillar ? (
        <div className="rounded-xl border dark:border-white/10 light:border-gray-200 p-8 text-center">
          <p className="text-lg font-semibold dark:text-untold-white light:text-black">{pillar.label} Catalog</p>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-500 max-w-md mx-auto">
            {pillar.label} content is managed via the events & news catalog pipeline.
            Full CMS integration for {pillar.label.toLowerCase()} is scheduled in Backend Sprint 2.
          </p>
          <a href={pillar.route} target="_blank" rel="noreferrer" className="inline-block mt-4 text-sm text-untold-gold hover:underline">
            Preview on site →
          </a>
        </div>
      ) : (
        <>
          <SearchFilter
            value={search}
            onChange={setSearch}
            placeholder={`Search ${pillar.label.toLowerCase()}...`}
          />

          {loading ? (
            <div className="h-64 rounded-xl skeleton" />
          ) : (
            <DataTable columns={columns} data={videoList} emptyMessage={`No ${pillar.label.toLowerCase()} found`} />
          )}
        </>
      )}

      <Modal open={showUpload} onClose={() => setShowUpload(false)} title={`Upload — ${pillar.label}`} wide>
        <VideoUploadForm
          categories={categoryList}
          defaultType={pillar.videoType || 'documentary'}
          defaultCategorySlug={pillar.slug}
          onSuccess={() => { setShowUpload(false); fetchContent(); }}
          onCancel={() => setShowUpload(false)}
        />
      </Modal>
    </div>
  );
}
