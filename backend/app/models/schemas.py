from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Any
from datetime import datetime
import uuid

class ScanRequest(BaseModel):
    url: HttpUrl

class Vulnerability(BaseModel):
    id: Optional[str] = None
    type: str
    description: str
    evidence: Optional[str] = None
    raw_severity: str

    class Config:
        from_attributes = True

class ScanResult(BaseModel):
    id: str
    url: str
    timestamp: datetime
    vulnerabilities: List[Any] = [] # Use Any for DB flex
    ml_severity_score: Optional[float] = 0.0
    confidence_score: Optional[float] = 0.0
    predicted_severity_label: Optional[str] = "Unknown"
    status: str
    logs: List[str] = []

    class Config:
        from_attributes = True

class Feedback(BaseModel):
    scan_id: str
    is_accurate: bool
    corrected_severity: Optional[str] = None
    analyst_comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True
