"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.interfaces.api import (
    analyze_router,
    conversation_router,
    faq_router,
    health_router,
    history_router,
    home_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    logger.info(f"Starting {settings.PROJECT_NAME} API server")

    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set - analysis will fail")

    yield

    logger.info(f"Shutting down {settings.PROJECT_NAME} API server")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI 기반 상담 코칭 및 품질 분석 시스템",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with tags for Swagger UI organization
app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(conversation_router)
app.include_router(faq_router)
app.include_router(home_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "cx-coach",
        "description": "AI 기반 상담 코칭 및 품질 분석 시스템",
        "docs": "/docs",
        "health": "/api/health",
    }
