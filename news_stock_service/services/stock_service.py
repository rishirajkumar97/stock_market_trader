import yfinance as yf
from sqlmodel import Session
from databases import engine
from models.stock import StockPrice
from datetime import datetime

FTSE_TICKER = "^FTSE"

def get_ftse_price():
    """Fetch the latest FTSE 100 price"""
    try:
        ticker = yf.Ticker(FTSE_TICKER)
        ftse_data = ticker.history(period="1d", interval="1m")
        return ftse_data["Close"].iloc[-1] if not ftse_data.empty else None
    except Exception as e:
        print(f"⚠️ Error fetching FTSE data: {e}")
        return None

def save_ftse_price():
    """Fetch and store FTSE 100 price"""
    price = get_ftse_price()
    if price is None:
        return

    with Session(engine) as session:
        stock_entry = StockPrice(timestamp=datetime.utcnow(), price=price)
        session.add(stock_entry)
        session.commit()
    
    print(f"📈 FTSE 100 price updated: {price}")