from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime

# Get database URL from environment, or fallback to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///omniquant.db")

# SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, index=True)
    predicted_date = Column(DateTime, default=datetime.datetime.utcnow)
    predicted_price = Column(Float)
    actual_price = Column(Float, nullable=True) # Filled later for drift monitoring
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
