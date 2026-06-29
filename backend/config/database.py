import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coffee.db")

if DATABASE_URL.startswith("mssql+pyodbc://"):
    engine_url = DATABASE_URL
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }
elif DATABASE_URL.startswith("sqlite"):
    engine_url = DATABASE_URL
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
    }
else:
    engine_url = f"mssql+pyodbc:///?odbc_connect={DATABASE_URL}"
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

engine = create_engine(engine_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
