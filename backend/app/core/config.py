import os
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(env_path, override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Phishing Email Detection System"
    API_V1_STR: str = "/api"
    
    # Server & CORS
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    FRONTEND_REDIRECT_URL: str = "http://localhost:5173"
    
    # Secret Key for Token Encryption (Fernet / AES)
    # Default provided for immediate testability, can be overridden in .env
    SECRET_KEY: str = "k7fN1u0kQ9Y3Z4_X2vA6bC8eD0fG2hJ4kL6mN8pQ0sU="
    
    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "phishing_detection_db"
    
    # ML Models Path
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ML_MODELS_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "ml_model", "saved_models")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        extra = "allow"

settings = Settings()
