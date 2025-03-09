from fastapi import FastAPI
from databases import create_db_and_tables
from scheduler.jobs import scheduler
from routers import news, stock
from fastapi_pagination import add_pagination

app = FastAPI()
add_pagination(app)

@app.on_event("startup")
def startup():
    create_db_and_tables()

    # ✅ Prevent duplicate scheduler starts
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
def shutdown():
    """Gracefully shutdown the scheduler when FastAPI stops."""
    scheduler.shutdown(wait=False)

app.include_router(news.router, prefix="/news", tags=["News"])
app.include_router(stock.router, prefix="/ftse", tags=["FTSE 100"])
