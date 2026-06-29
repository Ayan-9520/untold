/** Tiled sports backdrop for Netflix-style hero */

const SPORTS_TILES = [
  'https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=400&q=70',
  'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=400&q=70',
  'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&q=70',
  'https://images.unsplash.com/photo-1461896836934-ffe607ad7a85?w=400&q=70',
  'https://images.unsplash.com/photo-1624526267942-ab0ff8a3e972?w=400&q=70',
  'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=70',
  'https://images.unsplash.com/photo-1517649763962-0c62306601b7?w=400&q=70',
  'https://images.unsplash.com/photo-1551958219-acbc608c6377?w=400&q=70',
  'https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=400&q=70',
  'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=400&q=70',
  'https://images.unsplash.com/photo-1508098682722-e99b774a4f6e?w=400&q=70',
  'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=400&q=70',
  'https://images.unsplash.com/photo-1519315901367-f34ff9154487?w=400&q=70',
  'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=400&q=70',
  'https://images.unsplash.com/photo-1471295253337-36cecaee932c?w=400&q=70',
  'https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=400&q=70',
];

export function getHeroBackdropTiles(count = 40) {
  return Array.from({ length: count }, (_, i) => SPORTS_TILES[i % SPORTS_TILES.length]);
}
