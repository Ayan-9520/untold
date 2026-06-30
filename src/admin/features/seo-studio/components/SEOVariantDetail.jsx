function CopyBtn({ text, label = 'Copy' }) {
  return (
    <button
      type="button"
      onClick={() => navigator.clipboard?.writeText(text)}
      className="text-[10px] text-untold-gold hover:underline"
    >
      {label}
    </button>
  );
}

function MetaBlock({ title, children, copyText }) {
  return (
    <div className="rounded border dark:border-white/10 p-2 space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-[10px] uppercase tracking-wide text-untold-gold">{title}</span>
        {copyText && <CopyBtn text={copyText} />}
      </div>
      {children}
    </div>
  );
}

export default function SEOVariantDetail({ variant, expanded }) {
  if (!expanded) return null;

  const jsonExport = JSON.stringify({
    youtube_title: variant.youtube_title,
    meta_title: variant.meta_title,
    description: variant.description,
    keywords: variant.keywords,
    hashtags: variant.hashtags,
    tags: variant.tags,
    open_graph: variant.open_graph,
    twitter_cards: variant.twitter_cards,
    schema_org: variant.schema_org,
    seo_score: variant.seo_score,
    suggestions: variant.suggestions,
  }, null, 2);

  return (
    <div className="mt-3 space-y-2 border-t dark:border-white/10 pt-3">
      <MetaBlock title="YouTube Title" copyText={variant.youtube_title}>
        <p className="text-xs dark:text-white">{variant.youtube_title}</p>
      </MetaBlock>
      <MetaBlock title="Meta Title" copyText={variant.meta_title}>
        <p className="text-xs dark:text-white">{variant.meta_title}</p>
      </MetaBlock>
      <MetaBlock title="Description" copyText={variant.description}>
        <p className="text-xs dark:text-untold-muted whitespace-pre-wrap">{variant.description}</p>
      </MetaBlock>
      <MetaBlock title="Keywords" copyText={variant.keywords?.join(', ')}>
        <p className="text-xs dark:text-untold-muted">{variant.keywords?.join(', ')}</p>
      </MetaBlock>
      <MetaBlock title="Hashtags" copyText={variant.hashtags?.join(' ')}>
        <p className="text-xs dark:text-untold-muted">{variant.hashtags?.join(' ')}</p>
      </MetaBlock>
      <MetaBlock title="Tags" copyText={variant.tags?.join(', ')}>
        <p className="text-xs dark:text-untold-muted">{variant.tags?.join(', ')}</p>
      </MetaBlock>
      <MetaBlock title="OpenGraph" copyText={JSON.stringify(variant.open_graph, null, 2)}>
        <pre className="text-[10px] dark:text-untold-muted overflow-x-auto">{JSON.stringify(variant.open_graph, null, 2)}</pre>
      </MetaBlock>
      <MetaBlock title="Twitter Cards" copyText={JSON.stringify(variant.twitter_cards, null, 2)}>
        <pre className="text-[10px] dark:text-untold-muted overflow-x-auto">{JSON.stringify(variant.twitter_cards, null, 2)}</pre>
      </MetaBlock>
      <MetaBlock title="Schema.org" copyText={JSON.stringify(variant.schema_org, null, 2)}>
        <pre className="text-[10px] dark:text-untold-muted overflow-x-auto">{JSON.stringify(variant.schema_org, null, 2)}</pre>
      </MetaBlock>
      <div className="flex gap-2 pt-1">
        <CopyBtn text={jsonExport} label="Copy full JSON" />
      </div>
    </div>
  );
}
