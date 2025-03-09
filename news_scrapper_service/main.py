from fastapi import FastAPI, Depends, HTTPException
from databases import create_db_and_tables, get_session
from fetcher import fetch_news, save_news
from sqlmodel import Session, select
from models import NewsArticle, NewsArticleUpdate
from apscheduler.schedulers.background import BackgroundScheduler
import threading
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page, add_pagination

app = FastAPI()
add_pagination(app)

scheduler = BackgroundScheduler()

# Create DB Tables on Startup
@app.on_event("startup")
def startup():
    create_db_and_tables()
    fetch_and_store_news()
    # Check if scheduler is already running before starting
    if not scheduler.running:
        scheduler.add_job(fetch_and_store_news, "interval", minutes=30)
        scheduler.start()

@app.on_event("shutdown")
def shutdown():
    """Shutdown scheduler when FastAPI stops"""
    scheduler.shutdown()

def fetch_and_store_news():
    """Fetches news and saves it to the database"""
    articles = fetch_news()
    if articles:
        save_news(articles)

@app.get("/news", response_model=Page[NewsArticle])
def get_news(session: Session = Depends(get_session)):
    # query = select(NewsArticle).statement  # Convert SQLModel query to SQLAlchemy query
    return paginate(session, select(NewsArticle))

@app.patch("/news/{article_id}", response_model=NewsArticle)
def update_news_article(article_id: int, update_data: NewsArticleUpdate, session: Session = Depends(get_session)):
    """Update an existing news article's reward_signal, predicted_action, or actual_price_change."""
    article = session.get(NewsArticle, article_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Update only fields that are provided in the request
    if update_data.reward_signal is not None:
        article.reward_signal = update_data.reward_signal
    if update_data.predicted_action is not None:
        article.predicted_action = update_data.predicted_action
    if update_data.actual_price_change is not None:
        article.actual_price_change = update_data.actual_price_change

    session.add(article)
    session.commit()
    session.refresh(article)  # Get updated values
    return article

# Run API Server: uvicorn main:app --reload