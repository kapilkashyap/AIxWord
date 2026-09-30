"""
FastAPI dependency injection utilities.

This module provides dependency injection functions for FastAPI routes,
including orchestrator instances, settings, and other shared resources.
"""

from typing import Annotated

from fastapi import Depends

from backend.agents.orchestrator import PuzzleOrchestrator, get_orchestrator
from backend.api.services.solver import PuzzleSolver, get_solver
from backend.config import Settings, get_settings


def get_puzzle_orchestrator() -> PuzzleOrchestrator:
    """
    Get the singleton puzzle orchestrator instance.

    This dependency provides access to the PuzzleOrchestrator for
    puzzle generation and management operations.

    Returns:
        PuzzleOrchestrator instance
    """
    return get_orchestrator()


def get_app_settings() -> Settings:
    """
    Get the application settings.

    This dependency provides access to the application configuration.

    Returns:
        Settings instance
    """
    return get_settings()


def get_puzzle_solver() -> PuzzleSolver:
    """
    Get the singleton puzzle solver instance.

    This dependency provides access to the PuzzleSolver for
    AI-powered puzzle solving and hint generation.

    Returns:
        PuzzleSolver instance
    """
    return get_solver()


# Type aliases for dependency injection
OrchestratorDep = Annotated[PuzzleOrchestrator, Depends(get_puzzle_orchestrator)]
SettingsDep = Annotated[Settings, Depends(get_app_settings)]
SolverDep = Annotated[PuzzleSolver, Depends(get_puzzle_solver)]
