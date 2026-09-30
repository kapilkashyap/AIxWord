"""
FastAPI application entry point for AIxWord backend.

This module initializes the FastAPI application with all routes, middleware,
and configuration. It provides the main app instance used by uvicorn.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings

from .routes import health, puzzles

# Configure logging
settings = get_settings()
settings.configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting AIxWord backend application")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info(f"Default Grid Size: {settings.grid_size}x{settings.grid_size}")
    logger.info(f"Max Iterations: {settings.max_iterations}")
    logger.info(f"API Documentation: {'Enabled' if settings.enable_docs else 'Disabled'}")

    yield

    # Shutdown
    logger.info("Shutting down AIxWord backend application")


# Create FastAPI application
app = FastAPI(
    title="AIxWord API",
    description=(
        "AI-powered interactive crossword puzzle application with multi-agent system. "
        "Generate puzzles from topics, solve with AI assistance, and get hints."
    ),
    version="0.1.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Logs the error and returns a generic error response to the client.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(puzzles.router, prefix="/api/puzzles", tags=["Puzzles"])


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint redirect to API documentation.
    """
    return {
        "message": "AIxWord API",
        "version": "0.1.0",
        "docs": "/docs" if settings.enable_docs else None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
