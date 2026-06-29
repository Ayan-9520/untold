"""Shared text utilities."""

import re
import unicodedata


def slugify(text: str, max_length: int = 200) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:max_length] or "article"
