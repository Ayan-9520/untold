"""News CRUD, publishing workflow, and public queries."""

import json
import math
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.news import NewsArticle, NewsCategory, NewsStatus, NewsTag, NewsType
from app.schemas.news import NewsArticleDetailResponse, NewsArticleResponse, NewsCreateRequest, NewsListParams
from app.services.news_ai_service import NewsAIService
from app.utils.text import slugify


class NewsService:
    @staticmethod
    def list_articles(db: Session, params: NewsListParams) -> tuple[list[NewsArticle], int]:
        query = (
            db.query(NewsArticle)
            .options(joinedload(NewsArticle.category), joinedload(NewsArticle.tags))
            .filter(NewsArticle.status == NewsStatus.PUBLISHED)
        )

        if params.sport:
            query = query.filter(NewsArticle.sport.ilike(params.sport))

        if params.news_type:
            try:
                query = query.filter(NewsArticle.news_type == NewsType(params.news_type))
            except ValueError:
                pass

        if params.breaking is not None:
            query = query.filter(NewsArticle.is_breaking == params.breaking)

        if params.trending is not None:
            query = query.filter(NewsArticle.is_trending == params.trending)

        if params.search:
            term = f"%{params.search}%"
            query = query.filter(
                or_(NewsArticle.title.ilike(term), NewsArticle.excerpt.ilike(term), NewsArticle.summary.ilike(term))
            )

        total = query.count()
        articles = (
            query.order_by(
                NewsArticle.is_breaking.desc(),
                NewsArticle.published_at.desc().nullslast(),
                NewsArticle.created_at.desc(),
            )
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .all()
        )
        return articles, total

    @staticmethod
    def get_trending(db: Session, limit: int = 10) -> list[NewsArticle]:
        return (
            db.query(NewsArticle)
            .options(joinedload(NewsArticle.category), joinedload(NewsArticle.tags))
            .filter(NewsArticle.status == NewsStatus.PUBLISHED)
            .filter(or_(NewsArticle.is_trending.is_(True), NewsArticle.is_breaking.is_(True)))
            .order_by(NewsArticle.is_breaking.desc(), NewsArticle.views_count.desc(), NewsArticle.published_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_sport(db: Session, sport: str, limit: int = 20) -> list[NewsArticle]:
        return (
            db.query(NewsArticle)
            .options(joinedload(NewsArticle.category), joinedload(NewsArticle.tags))
            .filter(NewsArticle.status == NewsStatus.PUBLISHED, NewsArticle.sport.ilike(sport))
            .order_by(NewsArticle.published_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, article_id: int, increment_views: bool = True) -> NewsArticle:
        article = (
            db.query(NewsArticle)
            .options(joinedload(NewsArticle.category), joinedload(NewsArticle.tags))
            .filter(NewsArticle.id == article_id, NewsArticle.status == NewsStatus.PUBLISHED)
            .first()
        )
        if not article:
            raise NotFoundError("News article")

        if increment_views:
            article.views_count += 1
            db.commit()
            db.refresh(article)
        return article

    @staticmethod
    def get_admin_by_id(db: Session, article_id: int) -> NewsArticle:
        article = (
            db.query(NewsArticle)
            .options(joinedload(NewsArticle.category), joinedload(NewsArticle.tags))
            .filter(NewsArticle.id == article_id)
            .first()
        )
        if not article:
            raise NotFoundError("News article")
        return article

    @staticmethod
    def create_article(db: Session, data: NewsCreateRequest) -> NewsArticle:
        slug = NewsService._unique_slug(db, data.title)
        category = None
        if data.category_slug:
            category = db.query(NewsCategory).filter(NewsCategory.slug == data.category_slug).first()

        article = NewsArticle(
            slug=slug,
            title=data.title,
            excerpt=data.excerpt,
            content=data.content,
            sport=data.sport,
            news_type=data.news_type,
            status=NewsStatus.DRAFT,
            is_breaking=data.is_breaking,
            is_trending=data.is_trending,
            thumbnail_url=data.thumbnail_url,
            source_url=data.source_url,
            author=data.author,
            category_id=category.id if category else None,
        )
        db.add(article)
        db.flush()

        for tag_slug in data.tag_slugs:
            tag = db.query(NewsTag).filter(NewsTag.slug == tag_slug).first()
            if tag:
                article.tags.append(tag)

        db.commit()
        db.refresh(article)

        if data.auto_process_ai:
            NewsAIService.process_article(db, article)

        return article

    @staticmethod
    def publish_article(db: Session, article_id: int, approve: bool = True) -> NewsArticle:
        article = NewsService.get_admin_by_id(db, article_id)

        if article.status == NewsStatus.PUBLISHED:
            return article

        if article.status == NewsStatus.PENDING_REVIEW and not approve:
            raise BadRequestError("Article requires admin approval before publishing")

        if article.status == NewsStatus.DRAFT:
            if not article.ai_processed_at:
                NewsAIService.process_article(db, article)
            elif approve:
                article.status = NewsStatus.PENDING_REVIEW

        article.status = NewsStatus.PUBLISHED
        article.published_at = article.published_at or datetime.now(timezone.utc)
        if article.is_breaking:
            article.is_trending = True

        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def _unique_slug(db: Session, title: str) -> str:
        base = slugify(title)
        slug = base
        counter = 1
        while db.query(NewsArticle).filter(NewsArticle.slug == slug).first():
            slug = f"{base}-{counter}"
            counter += 1
        return slug

    @staticmethod
    def to_response(article: NewsArticle) -> NewsArticleResponse:
        return NewsArticleResponse.model_validate(article)

    @staticmethod
    def to_detail(article: NewsArticle) -> NewsArticleDetailResponse:
        headlines = []
        social = {}
        try:
            if article.headline_variants_json:
                headlines = json.loads(article.headline_variants_json)
            if article.social_captions_json:
                social = json.loads(article.social_captions_json)
        except json.JSONDecodeError:
            pass

        base = NewsService.to_response(article)
        return NewsArticleDetailResponse(
            **base.model_dump(),
            content=article.content,
            rewritten_content=article.rewritten_content,
            headline_variants=headlines,
            social_captions=social,
            seo_title=article.seo_title,
            seo_description=article.seo_description,
            seo_keywords=article.seo_keywords,
            status=article.status,
        )

    @staticmethod
    def pages(total: int, page_size: int) -> int:
        return math.ceil(total / page_size) if total else 0
