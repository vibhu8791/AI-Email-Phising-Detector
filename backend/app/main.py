import os
import sys
import logging
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings
from app.core.security import verify_access_token
from app.api import auth, emails, dashboard
from app.api.websocket import manager
from database.connection import db_service
from app.services.analyzer import analyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting up {settings.PROJECT_NAME} in '{settings.ENVIRONMENT}' environment...")
    # Initialize DB connection (enforces persistent MongoDB in production)
    await db_service.connect(settings.MONGODB_URL, settings.DATABASE_NAME)
    # Ensure ML model is loaded
    if not analyzer.is_loaded:
        analyzer._load_models()
    logger.info(f"Phishing ML Model loaded: {analyzer.is_loaded}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Full-stack AI Phishing Email Detection System with Google OAuth 2.0, Scikit-learn TF-IDF + Logistic Regression, WebSockets, and MongoDB.",
    lifespan=lifespan
)

# Configure CORS origins based on environment
cors_origins = settings.resolved_cors_origins if settings.is_production else ["*"]
logger.info(f"Configuring CORS with origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(emails.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

# Real-time WebSocket Endpoint for High-Priority Alerts
@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    user_id = None
    if token:
        payload = verify_access_token(token)
        if payload and payload.get("sub"):
            user_id = payload["sub"]

    await manager.connect(websocket, user_id=user_id)
    try:
        while True:
            # Keep-alive receive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket exception: {e}")
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "model_loaded": analyzer.is_loaded,
        "database_connected": not db_service.use_fallback
    }
