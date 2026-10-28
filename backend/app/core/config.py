import os
from pydantic_settings import BaseSettings
from typing import List, Union, Optional
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
    RAW_GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    RAW_FRONTEND_REDIRECT_URL: Optional[str] = os.getenv("FRONTEND_REDIRECT_URL")
    
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
    def is_production(self) -> bool:
        """Check if environment is set to production mode."""
        return (
            self.ENVIRONMENT.lower() in ("production", "prod")
            or self.REQUIRE_PERSISTENT_DB
            or bool(os.getenv("RENDER"))
            or bool(os.getenv("RENDER_EXTERNAL_URL"))
        )

    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        """
        Dynamically resolve OAuth callback URL.
        1. Explicit GOOGLE_REDIRECT_URI environment variable (if non-localhost or dev).
        2. Auto-derivation from Render's RENDER_EXTERNAL_URL.
        3. Strict guard: Never silently fallback to localhost in production mode.
        4. Safe default for local development.
        """
        uri = (self.RAW_GOOGLE_REDIRECT_URI or "").strip()
        is_local = not uri or "localhost" in uri or "127.0.0.1" in uri
        render_url = os.getenv("RENDER_EXTERNAL_URL", "").strip().rstrip("/")

        # If on Render, auto-derive canonical public redirect URI
        if is_local and render_url:
            return f"{render_url}/api/auth/google/callback"

        # Prevent silent fallback to localhost in production mode
        if is_local and self.is_production:
            raise RuntimeError(
                f"Production misconfiguration: GOOGLE_REDIRECT_URI cannot point to localhost ('{uri or 'unset'}'). "
                "Production OAuth requires a valid public HTTPS callback. Set GOOGLE_REDIRECT_URI="
                "https://phishshield-api-xgbd.onrender.com/api/auth/google/callback in your Render environment variables."
            )

        return uri or "http://localhost:8000/api/auth/google/callback"

    @GOOGLE_REDIRECT_URI.setter
    def GOOGLE_REDIRECT_URI(self, value: str):
        self.RAW_GOOGLE_REDIRECT_URI = value

    @property
    def FRONTEND_REDIRECT_URL(self) -> str:
        """
        Dynamically resolve post-OAuth frontend redirect URL.
        1. Explicit FRONTEND_REDIRECT_URL environment variable.
        2. Auto-derivation for Render production (https://ai-email-phising-detector.onrender.com).
        3. Strict guard: Never silently redirect to localhost in production mode.
        4. Safe default for local development (http://localhost:5173).
        """
        url = (self.RAW_FRONTEND_REDIRECT_URL or "").strip()
        is_local = not url or "localhost" in url or "127.0.0.1" in url

        # If running on Render, default to known production frontend if unset/localhost
        if is_local and (os.getenv("RENDER") or os.getenv("RENDER_EXTERNAL_URL")):
            return "https://ai-email-phising-detector.onrender.com"

        # Prevent silent fallback to localhost in production mode
        if is_local and self.is_production:
            raise RuntimeError(
                f"Production misconfiguration: FRONTEND_REDIRECT_URL cannot point to localhost ('{url or 'unset'}'). "
                "Set FRONTEND_REDIRECT_URL=https://ai-email-phising-detector.onrender.com in your Render environment variables."
            )

        return url or "http://localhost:5173"

    @FRONTEND_REDIRECT_URL.setter
    def FRONTEND_REDIRECT_URL(self, value: str):
        self.RAW_FRONTEND_REDIRECT_URL = value

    @property
    def effective_jwt_secret(self) -> str:
        """Return dedicated JWT_SECRET if configured, otherwise fallback to SECRET_KEY."""
        return self.JWT_SECRET.strip() if self.JWT_SECRET and self.JWT_SECRET.strip() else self.SECRET_KEY

    @property
    def resolved_cors_origins(self) -> List[str]:
        """Parse CORS origins as list even if provided as comma-separated string."""
        origins = []
        if isinstance(self.CORS_ORIGINS, str):
            origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        elif isinstance(self.CORS_ORIGINS, list):
            origins = list(self.CORS_ORIGINS)

        # In production mode, guarantee that FRONTEND_REDIRECT_URL is permitted in CORS
        try:
            fe_url = self.FRONTEND_REDIRECT_URL
            if fe_url and not any(loc in fe_url for loc in ("localhost", "127.0.0.1")):
                fe_origin = fe_url.rstrip("/")
                if fe_origin not in origins:
                    origins.append(fe_origin)
        except Exception:
            pass

        return origins

    class Config:
        extra = "allow"

settings = Settings()
