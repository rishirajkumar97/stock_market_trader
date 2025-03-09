from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from databases import get_session
from models.stock import StockPrice

router = APIRouter()

@router.get("/")
def get_ftse_history(session: Session = Depends(get_session)):
    """Fetch stored FTSE 100 prices"""
    return session.exec(select(StockPrice).order_by(StockPrice.timestamp.desc())).all()
