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
    user_id: str = "default_user"
    account_id: Optional[str] = None
    account_email: Optional[str] = None
    timestamp_utc: Optional[str] = None
    timestamp_epoch: Optional[float] = None
    date_display: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ThreatAlert(BaseModel):
    id: str
    email_id: str
    subject: str
    sender: str
    risk_score: float
    classification: str
    reasons: List[str] = []
    user_id: str = "default_user"
    account_id: Optional[str] = None
    account_email: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConnectedAccount(BaseModel):
    id: str
    user_id: str = "default_user"
    email: str
    display_name: Optional[str] = None
    access_token_encrypted: str
    refresh_token_encrypted: Optional[str] = None
    expires_at: Optional[str] = None
    scopes: List[str] = []
    status: str = "active"  # active, expired, revoked, error
    error_message: Optional[str] = None
    mode: str = "live"  # live, demo
    is_default: bool = False
    connected_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_synced_at: Optional[str] = None

class ConnectedAccountPublic(BaseModel):
    id: str
    user_id: str
    email: str
    display_name: str
    status: str
    mode: str
    is_default: bool
    connected_at: str
    last_synced_at: Optional[str] = None
    error_message: Optional[str] = None

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
    connected_accounts_count: int = 0
    connected_accounts: List[ConnectedAccountPublic] = []
    last_synced_at: Optional[str] = None
    database_mode: Optional[str] = None

