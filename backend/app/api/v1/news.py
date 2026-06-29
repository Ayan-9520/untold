import math

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models import User
from app.schemas.common import PaginatedResponse
from app.schemas.news import (
    NewsArticleDetailResponse,
    NewsArticleResponse,
    NewsCreateRequest,
    NewsFetchResponse,
    NewsListParams,
    NewsPublishRequest,
    NewsPublishResponse,
)
from app.services.news_service import NewsService

router = APIRouter(tags=["News"])


@router.get("/news", response_model=PaginatedResponse[NewsArticleResponse])
def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    sport: str | None = None,
    news_type: str | None = None,
    breaking: bool | None = None,
    trending: bool | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    params = NewsListParams(
        page=page,
        page_size=page_size,
        sport=sport,
        news_type=news_type,
        breaking=breaking,
        trending=trending,
        search=search,
    )
    articles, total = NewsService.list_articles(db, params)
    return PaginatedResponse(
        items=[NewsService.to_response(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        pages=NewsService.pages(total, page_size),
    )


@router.get("/news/trending", response_model=list[NewsArticleResponse])
def trending_news(
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
):
    articles = NewsService.get_trending(db, limit=limit)
    return [NewsService.to_response(a) for a in articles]


@router.get("/news/category/{sport}", response_model=list[NewsArticleResponse])
def news_by_category(
    sport: str,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    articles = NewsService.get_by_sport(db, sport, limit=limit)
    return [NewsService.to_response(a) for a in articles]


@router.get("/news/{article_id}", response_model=NewsArticleDetailResponse)
def get_news(article_id: int, db: Session = Depends(get_db)):
    article = NewsService.get_by_id(db, article_id)
    return NewsService.to_detail(article)


# --- Admin ---

admin_router = APIRouter(prefix="/admin/news", tags=["Admin News"])


@admin_router.post("", response_model=NewsArticleDetailResponse, status_code=status.HTTP_201_CREATED)
def admin_create_news(
    data: NewsCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    article = NewsService.create_article(db, data)
    return NewsService.to_detail(article)


@admin_router.post("/publish", response_model=NewsPublishResponse)
def admin_publish_news(
    data: NewsPublishRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    article = NewsService.publish_article(db, data.news_id, approve=data.approve)
    return NewsPublishResponse(
        message="Article published successfully",
        article=NewsService.to_detail(article),
    )


@admin_router.post("/fetch", response_model=NewsFetchResponse)
def admin_trigger_fetch(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    from app.workers.tasks import fetch_news_sources, process_pending_news_ai

    fetch_result = fetch_news_sources.delay()
    ai_result = process_pending_news_ai.delay()
    return NewsFetchResponse(
        message="News fetch and AI processing queued",
        task_id=fetch_result.id,
        sources_queued=0,
    )
