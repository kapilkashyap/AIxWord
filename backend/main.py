#!/usr/bin/env python3
"""
Main entry point for AIxWord backend application.

This module serves as the top-level entry point for the AIxWord backend.
It imports and exposes the FastAPI application instance for use by ASGI servers
like uvicorn, gunicorn, or hypercorn.

Usage:
    Development:
        python3 main.py

    Production (with uvicorn):
        uvicorn backend.main:app --host 0.0.0.0 --port 8000

    Production (with gunicorn):
        gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
"""

import sys
from pathlib import Path

# Ensure backend directory is in Python path
backend_dir = Path(__file__).parent
if str(backend_dir.parent) not in sys.path:
    sys.path.insert(0, str(backend_dir.parent))

# Import the FastAPI application
from backend.api.main import app  # noqa: E402

# Export app for ASGI servers
__all__ = ["app"]


if __name__ == "__main__":
    """
    Run the development server when executed directly.

    This is a convenience wrapper around uvicorn for development.
    For production, use a production-grade ASGI server directly.
    """
    import uvicorn

    from backend.config import get_settings

    settings = get_settings()

    # Configure logging before starting server
    settings.configure_logging()

    print("=" * 80)
    print("AIxWord Backend - Development Server")
    print("=" * 80)
    print("Environment: Development")
    print(f"Host: {settings.api_host}")
    print(f"Port: {settings.api_port}")
    print("")
    print("API Documentation:")
    if settings.enable_docs:
        print(f"  - Swagger UI: http://localhost:{settings.api_port}/docs")
        print(f"  - ReDoc:      http://localhost:{settings.api_port}/redoc")
    else:
        print("  - Documentation disabled (ENABLE_DOCS=false)")
    print("")
    print("Configuration:")
    print(f"  - OpenAI Model: {settings.openai_model}")
    print(f"  - Grid Size: {settings.grid_size}x{settings.grid_size}")
    print(f"  - Max Iterations: {settings.max_iterations}")
    print(f"  - Min Fill Rate: {settings.min_fill_rate}")
    print(f"  - Log Level: {settings.log_level}")
    print("")
    print("CORS Origins:")
    for origin in settings.cors_origins_list:
        print(f"  - {origin}")
    print("=" * 80)
    print()
    print("Starting server... (Press CTRL+C to quit)")
    print()

    # Run uvicorn with auto-reload for development
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
        access_log=True,
    )
