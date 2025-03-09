from apscheduler.schedulers.background import BackgroundScheduler
from services.news_service import fetch_and_store_news
from services.stock_service import save_ftse_price

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_news, "interval", minutes=30)
scheduler.add_job(save_ftse_price, "interval", minutes=1)
scheduler.start()