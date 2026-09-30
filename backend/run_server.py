#!/usr/bin/env python3
"""
Development server runner for AIxWord backend.

This script starts the FastAPI development server with auto-reload enabled.
For production deployment, use uvicorn directly or a production WSGI server.
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))

if __name__ == "__main__":
    import uvicorn

    from backend.config import get_settings

    settings = get_settings()

    print("=" * 70)
    print("AIxWord Backend Server")
    print("=" * 70)
    print(f"Host: {settings.api_host}")
    print(f"Port: {settings.api_port}")
    print(f"Docs: http://localhost:{settings.api_port}/docs")
    print(f"ReDoc: http://localhost:{settings.api_port}/redoc")
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"Grid Size: {settings.grid_size}x{settings.grid_size}")
    print("=" * 70)
    print()

    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
