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

class FeedbackDB(Base):
    __tablename__ = "feedback"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, index=True)
    is_accurate = Column(Boolean)
    corrected_severity = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

SQLALCHEMY_DATABASE_URL = "sqlite:///./wvs_storage.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
