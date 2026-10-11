import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings
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
    logger.info("Starting up AI Phishing Email Detection System...")
    # Initialize DB connection (with resilient fallback)
    await db_service.connect(settings.MONGODB_URL, settings.DATABASE_NAME)
    # Ensure ML model is loaded
    if not analyzer.is_loaded:
        analyzer._load_models()
    logger.info(f"Phishing ML Model loaded: {analyzer.is_loaded}")
    yield
    logger.info("Shutting down AI Phishing Email Detection System...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Full-stack AI Phishing Email Detection System with Google OAuth 2.0, Scikit-learn TF-IDF + Logistic Regression, WebSockets, and MongoDB.",
    lifespan=lifespan
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local dev frontends
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
async def websocket_alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep-alive receive
            data = await websocket.receive_text()
            # Echo or handle ping
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
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": analyzer.is_loaded,
        "database_connected": not db_service.use_fallback
    }
