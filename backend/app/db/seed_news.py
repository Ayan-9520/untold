"""Seed news categories, sources, and articles."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.news import (
    NewsArticle,
    NewsCategory,
    NewsSource,
    NewsSourceType,
    NewsStatus,
    NewsTag,
    NewsType,
)
from app.utils.text import slugify

NEWS_CATEGORIES = [
    ("Breaking News", "breaking-news", "Urgent sports headlines as they happen"),
    ("Match Updates", "match-updates", "Live scores, results, and match reports"),
    ("Feature Stories", "feature-stories", "In-depth sports journalism"),
    ("Exclusive UNTOLD Stories", "exclusive-untold", "Original reporting from the UNTOLD desk"),
]

DEFAULT_SOURCES = [
    ("BBC Sport RSS", NewsSourceType.RSS, "https://feeds.bbci.co.uk/sport/rss.xml", "Football"),
    ("ESPN Cricket RSS", NewsSourceType.RSS, "https://www.espncricinfo.com/rss/content/story/feeds/0.xml", "Cricket"),
    ("SportMonks Football", NewsSourceType.SPORTMONKS, "https://api.sportmonks.com/v3/football/news", "Football"),
    ("Sportradar Live", NewsSourceType.SPORTRADAR, None, "Football"),
    ("CricAPI Live", NewsSourceType.CRICAPI, None, "Cricket"),
]

SEED_ARTICLES = [
    {
        "title": "Kohli Fifty Steadies India at Lord's",
        "excerpt": "Captain reaches milestone as second Test hangs in balance on day two.",
        "sport": "Cricket",
        "news_type": NewsType.BREAKING,
        "is_trending": True,
        "is_breaking": True,
    },
    {
        "title": "Premier League Title Race: Final Day Drama",
        "excerpt": "Three teams still in contention as simultaneous kick-offs decide the crown.",
        "sport": "Football",
        "news_type": NewsType.BREAKING,
        "is_trending": True,
        "is_breaking": True,
    },
    {
        "title": "UFC 305: Main Event Walkouts Underway",
        "excerpt": "Las Vegas card delivers as challengers look to dethrone the champion.",
        "sport": "MMA",
        "news_type": NewsType.MATCH_UPDATE,
        "is_trending": True,
    },
    {
        "title": "Wimbledon Draw: Alcaraz Faces Tough Path",
        "excerpt": "Defending champion lands in same half as rising stars.",
        "sport": "Tennis",
        "news_type": NewsType.FEATURE,
    },
    {
        "title": "ICC World Cup 2026: Host Cities Announced",
        "excerpt": "Ten venues across India confirmed for cricket's biggest carnival.",
        "sport": "Cricket",
        "news_type": NewsType.FEATURE,
        "is_trending": True,
    },
    {
        "title": "Hamilton Targets Home Glory at Silverstone",
        "excerpt": "Seven-time champion eyes first British GP win with new team.",
        "sport": "Formula 1",
        "news_type": NewsType.FEATURE,
    },
    {
        "title": "UNTOLD Exclusive: The Dressing Room Truth",
        "excerpt": "Never-before-told stories from inside the world's biggest rivalries.",
        "sport": "Football",
        "news_type": NewsType.EXCLUSIVE,
        "is_trending": True,
    },
]

THUMBNAILS = {
    "Cricket": "https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=800&q=80",
    "Football": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80",
    "Tennis": "https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=800&q=80",
    "Formula 1": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80",
    "MMA": "https://images.unsplash.com/photo-1555597673-b21d5c48148c?w=800&q=80",
}


def seed_news_data(db: Session) -> None:
    if db.query(NewsCategory).first():
        return

    category_map: dict[str, NewsCategory] = {}
    for name, slug, desc in NEWS_CATEGORIES:
        cat = NewsCategory(name=name, slug=slug, description=desc)
        db.add(cat)
        category_map[slug] = cat
    db.flush()

    for name, source_type, url, sport in DEFAULT_SOURCES:
        db.add(
            NewsSource(
                name=name,
                source_type=source_type,
                url=url,
                sport=sport,
                is_active=True,
            )
        )
    db.flush()

    manual_source = NewsSource(
        name="UNTOLD Editorial",
        source_type=NewsSourceType.MANUAL,
        sport=None,
        is_active=True,
    )
    db.add(manual_source)
    db.flush()

    now = datetime.now(timezone.utc)
    for i, item in enumerate(SEED_ARTICLES):
        slug = slugify(item["title"])
        cat_slug = {
            NewsType.BREAKING: "breaking-news",
            NewsType.MATCH_UPDATE: "match-updates",
            NewsType.FEATURE: "feature-stories",
            NewsType.EXCLUSIVE: "exclusive-untold",
        }.get(item["news_type"], "feature-stories")

        article = NewsArticle(
            slug=slug,
            title=item["title"],
            excerpt=item["excerpt"],
            content=item["excerpt"],
            summary=item["excerpt"],
            sport=item["sport"],
            news_type=item["news_type"],
            status=NewsStatus.PUBLISHED,
            is_breaking=item.get("is_breaking", False),
            is_trending=item.get("is_trending", False),
            thumbnail_url=THUMBNAILS.get(item["sport"], THUMBNAILS["Cricket"]),
            author="UNTOLD Editorial",
            category_id=category_map[cat_slug].id,
            source_id=manual_source.id,
            published_at=now,
            views_count=1000 + i * 250,
        )
        db.add(article)

    for tag_name in ("breaking", "cricket", "football", "untold", "exclusive"):
        db.add(NewsTag(name=tag_name, slug=tag_name))

    db.commit()
