import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { FOOTER_CONTACT } from '../../data/siteConfig';

const PRODUCTION_HOSTS = new Set([
  'untoldoriginals.blog',
  'www.untoldoriginals.blog',
]);

function isProductionHost() {
  if (typeof window === 'undefined') return false;
  const host = window.location.hostname.toLowerCase();
  return PRODUCTION_HOSTS.has(host) || host.endsWith('.vercel.app');
}

function latLngToTile(lat, lng, zoom) {
  const n = 2 ** zoom;
  const x = Math.floor(((lng + 180) / 360) * n);
  const latRad = (lat * Math.PI) / 180;
  const y = Math.floor(
    ((1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2) * n,
  );
  return { x, y };
}

function OsmTileMap({ lat, lng }) {
  const zoom = 14;
  const tiles = useMemo(() => {
    const { x, y } = latLngToTile(lat, lng, zoom);
    return [-2, -1, 0, 1, 2].map((dx) => ({
      key: `${x + dx}-${y}`,
      url: `https://tile.openstreetmap.org/${zoom}/${x + dx}/${y}.png`,
    }));
  }, [lat, lng]);

  return (
    <div className="site-footer-map-tiles" aria-hidden="true">
      {tiles.map((tile) => (
        <img key={tile.key} src={tile.url} alt="" className="site-footer-map-tile" loading="lazy" />
      ))}
      <span className="site-footer-map-pin" />
      <span className="site-footer-map-attribution">© OpenStreetMap</span>
    </div>
  );
}

export default function FooterMap() {
  const { t } = useTranslation();
  const { mapLat, mapLng, mapQuery } = FOOTER_CONTACT;
  const useGoogleEmbed = isProductionHost();

  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(mapQuery)}`;
  const googleEmbedSrc = `https://www.google.com/maps?q=${mapLat},${mapLng}&hl=en&z=15&output=embed`;

  return (
    <div className="site-footer-map">
      {useGoogleEmbed ? (
        <iframe
          title="UNTOLD office location"
          src={googleEmbedSrc}
          className="site-footer-map-frame"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          allowFullScreen
        />
      ) : (
        <a
          href={mapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="site-footer-map-static"
          aria-label={t('footer.openInMaps', 'Open in Google Maps')}
        >
          <OsmTileMap lat={mapLat} lng={mapLng} />
        </a>
      )}
      <a
        href={mapsUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="site-footer-map-open"
      >
        {t('footer.openInMaps', 'Open in Google Maps')}
      </a>
    </div>
  );
}
