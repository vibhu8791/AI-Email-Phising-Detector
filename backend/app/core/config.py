import os
from pydantic_settings import BaseSettings
from typing import List, Union
from dotenv import load_dotenv

# Search for .env in current and parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
root_dir = os.path.dirname(backend_dir)

env_candidates = [
    os.path.join(root_dir, ".env"),
    os.path.join(backend_dir, ".env"),
]
for candidate in env_candidates:
    if os.path.exists(candidate):
        load_dotenv(candidate, override=True)
        break

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Phishing Email Detection System"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server & Networking
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
    FRONTEND_REDIRECT_URL: str = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:5173")
    
    # Cryptographic Secrets
    SECRET_KEY: str = os.getenv("SECRET_KEY", "k7fN1u0kQ9Y3Z4_X2vA6bC8eD0fG2hJ4kL6mN8pQ0sU=")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "168"))  # 7 days
    
    # Database Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "phishing_detection_db")
    REQUIRE_PERSISTENT_DB: bool = os.getenv("REQUIRE_PERSISTENT_DB", "false").lower() in ("true", "1", "yes")
    
    # ML Models Path
    BASE_DIR: str = backend_dir
    ML_MODELS_DIR: str = os.path.join(root_dir, "ml_model", "saved_models")

    @property
    def effective_jwt_secret(self) -> str:
        """Return dedicated JWT_SECRET if configured, otherwise fallback to SECRET_KEY."""
        return self.JWT_SECRET.strip() if self.JWT_SECRET and self.JWT_SECRET.strip() else self.SECRET_KEY

    @property
    def resolved_cors_origins(self) -> List[str]:
        """Parse CORS origins as list even if provided as comma-separated string."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

    @property
    def is_production(self) -> bool:
        """Check if environment is set to production."""
        return self.ENVIRONMENT.lower() in ("production", "prod") or self.REQUIRE_PERSISTENT_DB

    class Config:
        extra = "allow"

settings = Settings()
