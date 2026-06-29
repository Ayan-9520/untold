"""AI News Agent — summarize, rewrite, headlines, tags, SEO, social captions."""

import json
import logging
import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.news import NewsArticle, NewsStatus, NewsTag
from app.utils.text import slugify

logger = logging.getLogger("untold")
settings = get_settings()


class NewsAIService:
    @staticmethod
    def process_article(db: Session, article: NewsArticle) -> NewsArticle:
        """Run full AI pipeline on an article. Uses OpenAI when configured, else rule-based."""
        body = article.content or article.excerpt or article.title
        result = NewsAIService._generate_all(body, article.title, article.sport, article.news_type.value)

        article.summary = result["summary"]
        article.rewritten_content = result["rewritten_content"]
        article.excerpt = article.excerpt or result["summary"][:280]
        article.headline_variants_json = json.dumps(result["headlines"])
        article.social_captions_json = json.dumps(result["social_captions"])
        article.seo_title = result["seo"]["title"]
        article.seo_description = result["seo"]["description"]
        article.seo_keywords = result["seo"]["keywords"]
        article.ai_metadata_json = json.dumps(result["metadata"])
        article.ai_processed_at = datetime.now(timezone.utc)

        if article.status == NewsStatus.DRAFT:
            article.status = NewsStatus.PENDING_REVIEW

        NewsAIService._sync_tags(db, article, result["tags"])
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def _generate_all(body: str, title: str, sport: str, news_type: str) -> dict:
        if settings.openai_api_key:
            try:
                return NewsAIService._openai_generate(body, title, sport, news_type)
            except Exception as exc:
                logger.warning("OpenAI news agent failed, using fallback: %s", exc)

        return NewsAIService._fallback_generate(body, title, sport, news_type)

    @staticmethod
    def _openai_generate(body: str, title: str, sport: str, news_type: str) -> dict:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = f"""You are the UNTOLD sports news AI editor. Process this article.

Sport: {sport}
Type: {news_type}
Title: {title}
Body: {body[:4000]}

Return JSON with keys:
- summary (2-3 sentences)
- rewritten_content (editorial rewrite, 2-4 paragraphs, UNTOLD voice)
- headlines (array of 3 punchy headlines)
- tags (array of 5 lowercase tags)
- seo: {{title, description, keywords}}
- social_captions: {{twitter, instagram, facebook}}
"""
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a sports news AI editor for UNTOLD OTT. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        data = json.loads(response.choices[0].message.content or "{}")
        return {
            "summary": data.get("summary", ""),
            "rewritten_content": data.get("rewritten_content", body),
            "headlines": data.get("headlines", [title]),
            "tags": data.get("tags", []),
            "seo": data.get("seo", {}),
            "social_captions": data.get("social_captions", {}),
            "metadata": {"provider": "openai", "model": settings.openai_model},
        }

    @staticmethod
    def _fallback_generate(body: str, title: str, sport: str, news_type: str) -> dict:
        sentences = re.split(r"(?<=[.!?])\s+", body.strip())
        summary = " ".join(sentences[:2]) if sentences else title
        rewritten = f"{summary}\n\nUNTOLD brings you the story behind the headlines in {sport}."
        type_label = news_type.replace("_", " ").title()
        headlines = [
            title,
            f"UNTOLD: {title}",
            f"{sport} — {title[:80]}",
        ]
        tags = list(
            dict.fromkeys(
                [
                    slugify(sport),
                    slugify(news_type),
                    "sports",
                    "untold",
                    slugify(type_label),
                ]
            )
        )[:5]

        return {
            "summary": summary,
            "rewritten_content": rewritten,
            "headlines": headlines,
            "tags": tags,
            "seo": {
                "title": f"{title} | UNTOLD {sport}",
                "description": summary[:160],
                "keywords": f"{sport}, sports news, UNTOLD, {news_type}",
            },
            "social_captions": {
                "twitter": f"🔥 {title} — The story behind the glory. #UNTOLD #{slugify(sport)}",
                "instagram": f"{title}\n\n{summary[:200]}\n\n#UNTOLD #{slugify(sport)} #SportsNews",
                "facebook": f"{title}\n\n{summary}",
            },
            "metadata": {"provider": "rule-based", "model": "fallback"},
        }

    @staticmethod
    def _sync_tags(db: Session, article: NewsArticle, tag_names: list[str]) -> None:
        article.tags.clear()
        for name in tag_names:
            clean = name.strip().lower()
            if not clean:
                continue
            tag_slug = slugify(clean, max_length=80)
            tag = db.query(NewsTag).filter(NewsTag.slug == tag_slug).first()
            if not tag:
                tag = NewsTag(name=clean, slug=tag_slug)
                db.add(tag)
                db.flush()
            article.tags.append(tag)
