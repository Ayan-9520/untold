"""Heuristic SEO scoring for demo provider."""

from __future__ import annotations


def score_variant(
    *,
    youtube_title: str,
    meta_title: str,
    description: str,
    keywords: list[str],
    hashtags: list[str],
) -> tuple[int, list[str]]:
    score = 50
    suggestions: list[str] = []

    if 40 <= len(youtube_title) <= 70:
        score += 12
    else:
        suggestions.append("YouTube title works best between 40–70 characters.")

    if len(meta_title) <= 60:
        score += 8
    else:
        suggestions.append("Meta title should stay under 60 characters.")

    if 120 <= len(description) <= 320:
        score += 10
    elif len(description) < 120:
        suggestions.append("Expand description for richer keyword coverage.")
    else:
        suggestions.append("Trim description — front-load the hook in first 160 chars.")

    if 3 <= len(keywords) <= 12:
        score += 8
    else:
        suggestions.append("Use 3–12 focused keywords.")

    if hashtags:
        score += min(8, len(hashtags) * 2)
    else:
        suggestions.append("Add platform hashtags for discoverability.")

    if any(kw.lower() in description.lower() for kw in keywords[:3]):
        score += 6
    else:
        suggestions.append("Weave primary keywords into the description naturally.")

    return min(100, score), suggestions
