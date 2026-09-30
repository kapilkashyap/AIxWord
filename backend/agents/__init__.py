"""
Multi-agent system for crossword puzzle generation.

This package contains the LangGraph workflow and agents for generating
crossword puzzles using a multi-agent architecture.
"""

from .orchestrator import (
    PuzzleGenerationRequest,
    PuzzleGenerationResult,
    PuzzleOrchestrator,
    create_orchestrator,
    get_orchestrator,
)
from .planner import PlannerAction, PlannerAgent
from .state import AgentState, PlacementPlan, PuzzleRequirements, WordCandidate
from .word_generator import WordGenerationResult, WordGeneratorAction, WordGeneratorAgent
from .workflow import CrosswordWorkflow, get_workflow

__all__ = [
    # State models
    "AgentState",
    "PuzzleRequirements",
    "WordCandidate",
    "PlacementPlan",
    # Agents
    "PlannerAgent",
    "PlannerAction",
    "WordGeneratorAgent",
    "WordGeneratorAction",
    "WordGenerationResult",
    # Workflow
    "CrosswordWorkflow",
    "get_workflow",
    # Orchestrator
    "PuzzleOrchestrator",
    "PuzzleGenerationRequest",
    "PuzzleGenerationResult",
    "get_orchestrator",
    "create_orchestrator",
]
