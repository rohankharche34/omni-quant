from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import datetime

# Get database URL from environment, or fallback to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///omniquant.db")

# SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    price = Column(Float)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    algorithm = Column(String) # 'ARIMA' or 'GARCH'
    parameters = Column(JSON) # e.g., {'p': 1, 'd': 1, 'q': 1}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    arima_version_id = Column(Integer, ForeignKey("model_versions.id"))
    garch_version_id = Column(Integer, ForeignKey("model_versions.id"))
    training_start = Column(DateTime)
    training_end = Column(DateTime)
    execution_time_ms = Column(Float)
    metrics = Column(JSON) # e.g., {'arima_aic': 123.4, 'garch_aic': 56.7}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    predicted_date = Column(DateTime)
    predicted_price = Column(Float)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    volatility = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
