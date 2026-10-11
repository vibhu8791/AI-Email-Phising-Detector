from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class UrlAnalysisItem(BaseModel):
    url: str
    hostname: str
    risk_score: float
    is_suspicious: bool
    indicators: List[str] = []

class EmailRecord(BaseModel):
    id: str
    message_id: Optional[str] = None
    subject: str
    sender: str
    recipient: Optional[str] = None
    date: str
    snippet: Optional[str] = None
    body_plain: str
    body_html: Optional[str] = None
    extracted_urls: List[str] = []
    ml_phishing_probability: float = 0.0
    heuristic_score: float = 0.0
    risk_score: float = 0.0
    classification: str = "SAFE"  # SAFE, SUSPICIOUS, PHISHING
    detected_flags: List[str] = []
    keyword_matches: Dict[str, List[str]] = {}
    url_details: List[UrlAnalysisItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ThreatAlert(BaseModel):
    id: str
    email_id: str
    subject: str
    sender: str
    risk_score: float
    classification: str
    reasons: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserAuthToken(BaseModel):
    email: str
    access_token_encrypted: str
    refresh_token_encrypted: Optional[str] = None
    expires_at: Optional[str] = None
    scopes: List[str] = []
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_synced_at: Optional[datetime] = None

class DashboardStats(BaseModel):
    total_scanned: int
    safe_count: int
    suspicious_count: int
    phishing_count: int
    avg_risk_score: float
    is_gmail_connected: bool
    connected_email: Optional[str] = None
    last_synced_at: Optional[str] = None
