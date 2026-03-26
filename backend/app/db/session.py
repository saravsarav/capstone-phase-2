from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class ScanResultDB(Base):
    __tablename__ = "scans"
    
    id = Column(String, primary_key=True, index=True)
    url = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    vulnerabilities = Column(JSON)
    ml_severity_score = Column(Float)
    confidence_score = Column(Float)
    predicted_severity_label = Column(String)
    status = Column(String)
    logs = Column(JSON, default=lambda: [])

class UserDB(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FeedbackDB(Base):
    __tablename__ = "feedback"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, index=True)
    is_accurate = Column(Boolean)
    corrected_severity = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wvs_storage.db")
# For PostgreSQL with SQLAlchemy, often need to fix "postgres://" vs "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
# If it's SQLite, need to add "check_same_thread"
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
