from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from databases import get_session
from models.news import NewsArticle, NewsArticleUpdate
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

router = APIRouter()

@router.get("/", response_model=Page[NewsArticle])
def get_news(session: Session = Depends(get_session)):
    """Fetch stored news articles"""
    return paginate(session, select(NewsArticle))

@router.patch("/{article_id}", response_model=NewsArticle)
def update_news_article(article_id: int, update_data: NewsArticleUpdate, session: Session = Depends(get_session)):
    """Update an existing news article's reward_signal, predicted_action, or actual_price_change."""
    article = session.get(NewsArticle, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(article, key, value)

    session.commit()
    session.refresh(article)
    return article