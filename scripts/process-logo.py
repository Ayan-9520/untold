"""Process UNTOLD logo: clean transparent BG + crisp PNG exports."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "public" / "brand"
SOURCE = BRAND / "untold-logo-source.png"
APP_SOURCE = BRAND / "untold-app-icon-source.png"


def remove_bg_luminance(img: Image.Image, floor: int = 22, power: float = 0.88) -> Image.Image:
    """Make black/dark background transparent while keeping metallic letter detail."""
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    span = max(1, 255 - floor)

    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]
            peak = max(r, g, b)
            if peak <= floor:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                alpha = min(255, int(255 * ((peak - floor) / span) ** power))
                pixels[x, y] = (r, g, b, alpha)

    return img


def trim_transparent(img: Image.Image, padding: int = 6) -> Image.Image:
    bbox = img.getbbox()
    if not bbox:
        return img
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)
    return img.crop((left, top, right, bottom))


def split_wordmark(full: Image.Image) -> Image.Image:
    w, h = full.size
    alpha = full.split()[-1]
    row_counts = [sum(alpha.getpixel((x, y)) for x in range(w)) for y in range(h)]

    search_start = int(h * 0.55)
    gap_y = search_start
    min_count = float("inf")
    for y in range(search_start, int(h * 0.82)):
        if row_counts[y] < min_count:
            min_count = row_counts[y]
            gap_y = y

    wordmark = full.crop((0, 0, w, max(gap_y - 4, int(h * 0.62))))
    return trim_transparent(wordmark, padding=4)


def make_compact(wordmark: Image.Image, size: int = 512) -> Image.Image:
    wm_w, wm_h = wordmark.size
    pad = max(20, int(min(wm_w, wm_h) * 0.06))
    side = max(wm_w, wm_h) + pad * 2
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(wordmark, ((side - wm_w) // 2, (side - wm_h) // 2), wordmark)
    return square.resize((size, size), Image.Resampling.LANCZOS)


def save_png(img: Image.Image, path: Path) -> None:
    img.save(path, "PNG", compress_level=3)


def remove_interior_black(img: Image.Image, threshold: int = 42) -> Image.Image:
    """Remove leftover opaque black inside icon frame after luminance key."""
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0 and r <= threshold and g <= threshold and b <= threshold:
                pixels[x, y] = (0, 0, 0, 0)
    return img


def process_app_icon(floor: int = 26) -> Image.Image:
    src = Image.open(APP_SOURCE)
    icon = remove_interior_black(
        trim_transparent(remove_bg_luminance(src, floor=floor), padding=4)
    )
    # Square crop for consistent header sizing
    w, h = icon.size
    side = max(w, h)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(icon, ((side - w) // 2, (side - h) // 2), icon)
    return square.resize((256, 256), Image.Resampling.LANCZOS)


def main() -> None:
    src = Image.open(SOURCE)
    full = trim_transparent(remove_bg_luminance(src))
    wordmark = split_wordmark(full)
    compact = make_compact(wordmark, size=512)

    paths = {
        "full": BRAND / "untold-logo.png",
        "wordmark": BRAND / "untold-logo-wordmark.png",
        "compact": BRAND / "untold-logo-compact.png",
    }

    save_png(full, paths["full"])
    save_png(wordmark, paths["wordmark"])
    save_png(compact, paths["compact"])

    if APP_SOURCE.exists():
        app_icon = process_app_icon()
        app_path = BRAND / "untold-app-icon.png"
        save_png(app_icon, app_path)
        # Header + app surfaces use the official app icon
        save_png(app_icon, paths["compact"])
        print(f"app-icon: {app_icon.size} -> {app_path.name}")

    for name, path in paths.items():
        im = Image.open(path)
        px = im.convert("RGBA").load()
        w, h = im.size
        bad = sum(
            1 for y in range(h) for x in range(w)
            if px[x, y][3] > 200 and max(px[x, y][:3]) < 45
        )
        print(f"{name}: {im.size} opaque-black={bad} -> {path.name}")


if __name__ == "__main__":
    main()
