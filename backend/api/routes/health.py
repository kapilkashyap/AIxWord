"""
Health check endpoints.

This module provides health check and status endpoints for monitoring
the application's health and readiness.
"""

import logging
from typing import Any

from fastapi import APIRouter, status

from backend.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Any],
    summary="Health check",
    description="Check if the API is running and healthy",
)
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.

    Returns basic health status and application information.

    Returns:
        Dictionary with health status and metadata
    """
    settings = get_settings()

    return {
        "status": "healthy",
        "service": "aixword-backend",
        "version": "0.1.0",
        "config": {
            "grid_size": settings.grid_size,
            "max_iterations": settings.max_iterations,
            "openai_model": settings.openai_model,
        },
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],
    summary="Readiness check",
    description="Check if the API is ready to accept requests",
)
async def readiness_check() -> dict[str, str]:
    """
    Readiness check endpoint.

    Verifies that all required services and dependencies are available.

    Returns:
        Dictionary with readiness status
    """
    # In a production system, this would check:
    # - Database connectivity
    # - External API availability (OpenAI)
    # - Cache availability
    # For now, we just return ready

    return {
        "status": "ready",
        "message": "Service is ready to accept requests",
    }
