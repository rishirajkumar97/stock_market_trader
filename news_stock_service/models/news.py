from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class NewsArticle(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    content: str
    url: str
    source: str
    published_at: datetime
    sentiment_score: float
    sentiment_label: str
    predicted_action: str = "Hold"
    actual_price_change: float = 0.0
    reward_signal: float = 0.0

class NewsArticleUpdate(SQLModel):
    """NewsArticle Update Schema for updating reward_signal, predicted_action, and actual_price_change."""
    reward_signal: Optional[float] = None
    predicted_action: Optional[str] = None  # "Buy", "Sell", "Hold"
    actual_price_change: Optional[float] = None