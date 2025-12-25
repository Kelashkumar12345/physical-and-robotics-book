"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.api import health, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    settings = get_settings()
    if settings.debug:
        print("Starting Physical AI Book API in debug mode...")
    yield
    # Shutdown
    if settings.debug:
        print("Shutting down Physical AI Book API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Physical AI Book RAG Chatbot API",
        description="RAG-powered chatbot API for the Physical AI & Humanoid Robotics Book",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["System"])
    app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

    return app


app = create_app()
