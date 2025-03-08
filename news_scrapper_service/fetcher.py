import requests
import os
import re
from dotenv import load_dotenv
from sqlmodel import Session, select
from databases import engine
from models import NewsArticle
from datetime import datetime
from bs4 import BeautifulSoup
from sentiment import sentiment_analyzer

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")
BASE_URL = "https://newsapi.org/v2/everything"
def is_truncated(content: str) -> bool:
    """Detects if content is truncated based on '[+ number chars]' pattern."""
    return bool(re.search(r"\[\+\s*\d+\s*chars\]", content))

def get_last_published_at():
    """Retrieve the latest published_at timestamp from the database"""
    with Session(engine) as session:
        latest_article = session.exec(select(NewsArticle).order_by(NewsArticle.published_at.desc())).first()
        return latest_article.published_at if latest_article else None

def fetch_news():
    """Fetches news from NewsAPI starting from the latest saved article"""
    last_published_at = get_last_published_at()
    
    params = {
        "q": "london stock exchange news",
        "apiKey": API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10
    }
    
    if last_published_at:
        params["from"] = last_published_at.isoformat()  # Fetch news from the last recorded timestamp
    
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()["articles"]
    else:
        print("Error fetching news:", response.json())
        return None

def get_full_article(url):
    """Scrapes the full article text from the URL"""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract main content (this may need adjustments for different sites)
        paragraphs = soup.find_all("p")
        full_text = " ".join([p.text for p in paragraphs])
        return full_text if full_text else None

    except Exception as e:
        print(f"Failed to fetch full article: {e}")
        return None

def save_news(articles):
    """Saves news articles with full content and sentiment analysis"""
    with Session(engine) as session:
        new_articles = []
        texts = []  # To store text for batch processing
        
        for article in articles:
            existing = session.exec(select(NewsArticle).where(NewsArticle.url == article["url"])).first()
            if not existing:
                full_content = article.get("content", "")

                # If content is truncated, fetch full article
                if not full_content or is_truncated(full_content):
                    print(f"🔍 Fetching full content for: {article['title']}")
                    full_content = get_full_article(article["url"]) or article["description"]

                # Store for batch sentiment processing
                texts.append(full_content)
                new_articles.append(article)

        # Run batch sentiment analysis
        if texts:
            sentiment_results = sentiment_analyzer.analyze_sentiment(texts)

        # Save processed articles with sentiment scores
        for i, article in enumerate(new_articles):
            sentiment_score, sentiment_label = sentiment_results[i]
            print(sentiment_score)
            news_entry = NewsArticle(
                title=article["title"],
                description=article["description"],
                content=texts[i],
                url=article["url"],
                source=article["source"]["name"],
                published_at=datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
                sentiment_score=sentiment_score[2] - sentiment_score[0],  # Positive - Negative
                sentiment_label=sentiment_label
            )
            session.add(news_entry)

        session.commit()
