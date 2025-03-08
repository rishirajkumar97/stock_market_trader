from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = "sqlite:///news.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Initialize the database and tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Creates a session for database transactions"""
    with Session(engine) as session:
        yield session