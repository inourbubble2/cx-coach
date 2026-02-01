# FastAPI routes

from app.interfaces.api.analyze_routes import router as analyze_router
from app.interfaces.api.conversation_routes import router as conversation_router
from app.interfaces.api.faq_routes import router as faq_router
from app.interfaces.api.health_routes import router as health_router
from app.interfaces.api.history_routes import router as history_router
from app.interfaces.api.home_routes import router as home_router

__all__ = [
    "analyze_router",
    "conversation_router",
    "faq_router",
    "health_router",
    "health_router",
    "history_router",
    "home_router",
]
