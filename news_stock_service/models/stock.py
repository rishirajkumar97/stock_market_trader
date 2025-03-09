from sqlmodel import SQLModel, Field
from datetime import datetime

class StockPrice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    price: float