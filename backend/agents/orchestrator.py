"""
Orchestrator for crossword puzzle generation workflow.

This module provides a high-level interface for managing the multi-agent
crossword puzzle generation workflow. It coordinates the PlannerAgent and
WordGeneratorAgent through the LangGraph workflow, providing simplified
APIs for puzzle generation, monitoring, and result retrieval.
"""

import logging
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from domain import CrosswordGrid

from .planner import PlannerAgent
from .state import AgentState
from .word_generator import WordGeneratorAgent
from .workflow import CrosswordWorkflow

logger = logging.getLogger(__name__)


class PuzzleGenerationRequest(BaseModel):
    """
    Request for puzzle generation.

    Attributes:
        topic: Topic for puzzle generation
        grid_size: Size of the grid (NxN)
        min_words: Minimum number of words to place
        max_words: Maximum number of words to place
        difficulty: Difficulty level
        max_iterations: Maximum iterations allowed
    """
    topic: str = Field(..., description="Topic for puzzle generation")
    grid_size: int = Field(default=8, ge=4, le=20, description="Grid size (NxN)")
    min_words: int = Field(default=8, ge=4, description="Minimum number of words")
    max_words: int = Field(default=15, ge=4, description="Maximum number of words")
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Difficulty level"
    )
    max_iterations: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum iterations allowed"
    )


class PuzzleGenerationResult(BaseModel):
    """
    Result of puzzle generation.

    Attributes:
        success: Whether generation was successful
        grid: Generated crossword grid (if successful)
        status: Final workflow status
        word_count: Number of words placed
        fill_rate: Grid fill rate (0.0 to 1.0)
        iterations: Number of iterations executed
        error_message: Error message (if failed)
        metadata: Additional metadata from generation
    """
    success: bool = Field(..., description="Whether generation was successful")
    grid: Optional[dict[str, Any]] = Field(
        default=None,
        description="Serialized crossword grid"
    )
    status: str = Field(..., description="Final workflow status")
    word_count: int = Field(default=0, ge=0, description="Number of words placed")
    fill_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Grid fill rate")
    iterations: int = Field(default=0, ge=0, description="Iterations executed")
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class PuzzleOrchestrator:
    """
    High-level orchestrator for crossword puzzle generation.

    This class provides a simplified interface for:
    1. Generating puzzles with various configurations
    2. Monitoring generation progress
    3. Retrieving and managing results
    4. Handling errors and retries

    The orchestrator manages the LangGraph workflow and coordinates
    the PlannerAgent and WordGeneratorAgent.
    """

    def __init__(
        self,
        planner_agent: Optional[PlannerAgent] = None,
        word_generator_agent: Optional[WordGeneratorAgent] = None,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            planner_agent: PlannerAgent instance (creates default if not provided)
            word_generator_agent: WordGeneratorAgent instance (creates default if not provided)
        """
        self.planner_agent = planner_agent or PlannerAgent()
        self.word_generator_agent = word_generator_agent or WordGeneratorAgent()

        # Create workflow with agents
        self.workflow = CrosswordWorkflow(
            planner_agent=self.planner_agent,
            word_generator_agent=self.word_generator_agent,
        )

        logger.info("PuzzleOrchestrator initialized with workflow and agents")

    def generate_puzzle(
        self,
        request: PuzzleGenerationRequest
    ) -> PuzzleGenerationResult:
        """
        Generate a crossword puzzle synchronously.

        This method orchestrates the entire puzzle generation process:
        1. Validates the request
        2. Executes the LangGraph workflow
        3. Monitors progress
        4. Returns the final result

        Args:
            request: Puzzle generation request with parameters

        Returns:
            PuzzleGenerationResult with the generated puzzle or error
        """
        logger.info(
            f"Starting puzzle generation: topic='{request.topic}', "
            f"grid_size={request.grid_size}x{request.grid_size}, "
            f"difficulty={request.difficulty}"
        )

        try:
            # Execute workflow
            final_state = self.workflow.generate_puzzle(
                topic=request.topic,
                grid_size=request.grid_size,
                min_words=request.min_words,
                max_words=request.max_words,
                difficulty=request.difficulty,
                max_iterations=request.max_iterations,
            )

            # Convert state to result
            result = self._state_to_result(final_state)

            logger.info(
                f"Puzzle generation completed: success={result.success}, "
                f"words={result.word_count}, fill_rate={result.fill_rate:.2%}"
            )

            return result

        except Exception as e:
            logger.error(f"Puzzle generation failed: {e}", exc_info=True)
            return PuzzleGenerationResult(
                success=False,
                status="failed",
                error_message=str(e),
            )

    async def generate_puzzle_async(
        self,
        request: PuzzleGenerationRequest
    ) -> PuzzleGenerationResult:
        """
        Generate a crossword puzzle asynchronously.

        This method provides async support for puzzle generation,
        allowing non-blocking execution in async contexts.

        Args:
            request: Puzzle generation request with parameters

        Returns:
            PuzzleGenerationResult with the generated puzzle or error
        """
        logger.info(
            f"Starting async puzzle generation: topic='{request.topic}', "
            f"grid_size={request.grid_size}x{request.grid_size}"
        )

        try:
            # Execute workflow asynchronously
            final_state = await self.workflow.generate_puzzle_async(
                topic=request.topic,
                grid_size=request.grid_size,
                min_words=request.min_words,
                max_words=request.max_words,
                difficulty=request.difficulty,
                max_iterations=request.max_iterations,
            )

            # Convert state to result
            result = self._state_to_result(final_state)

            logger.info(
                f"Async puzzle generation completed: success={result.success}, "
                f"words={result.word_count}"
            )

            return result

        except Exception as e:
            logger.error(f"Async puzzle generation failed: {e}", exc_info=True)
            return PuzzleGenerationResult(
                success=False,
                status="failed",
                error_message=str(e),
            )

    def _state_to_result(self, state: AgentState) -> PuzzleGenerationResult:
        """
        Convert AgentState to PuzzleGenerationResult.

        Args:
            state: Final agent state from workflow

        Returns:
            PuzzleGenerationResult with extracted information
        """
        # Determine success
        success = (
            state.status == "completed" and
            state.is_requirements_met() and
            state.error_message is None
        )

        # Get grid
        grid = state.get_grid()
        grid_dict = grid.to_dict() if grid else None

        # Build result
        result = PuzzleGenerationResult(
            success=success,
            grid=grid_dict,
            status=state.status,
            word_count=state.get_word_count(),
            fill_rate=state.get_fill_rate(),
            iterations=state.iteration,
            error_message=state.error_message,
            metadata=state.metadata,
        )

        return result

    def validate_request(self, request: PuzzleGenerationRequest) -> tuple[bool, Optional[str]]:
        """
        Validate a puzzle generation request.

        Args:
            request: Request to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check grid size
        if request.grid_size < 4 or request.grid_size > 20:
            return False, f"Grid size must be between 4 and 20, got {request.grid_size}"

        # Check word counts
        if request.min_words < 4:
            return False, f"min_words must be at least 4, got {request.min_words}"

        if request.max_words < request.min_words:
            return False, f"max_words ({request.max_words}) must be >= min_words ({request.min_words})"

        # Check if word counts are feasible for grid size
        max_possible_words = (request.grid_size * 2) - 2  # Rough estimate
        if request.min_words > max_possible_words:
            return False, (
                f"min_words ({request.min_words}) may be too high for "
                f"grid size {request.grid_size}x{request.grid_size}"
            )

        # Check topic
        if not request.topic or not request.topic.strip():
            return False, "Topic cannot be empty"

        # Check iterations
        if request.max_iterations < 1 or request.max_iterations > 100:
            return False, f"max_iterations must be between 1 and 100, got {request.max_iterations}"

        return True, None

    def get_grid_from_result(self, result: PuzzleGenerationResult) -> Optional[CrosswordGrid]:
        """
        Extract CrosswordGrid from a generation result.

        Args:
            result: Generation result

        Returns:
            CrosswordGrid instance or None if not available
        """
        if not result.success or result.grid is None:
            return None

        try:
            return CrosswordGrid.from_dict(result.grid)
        except Exception as e:
            logger.error(f"Failed to deserialize grid: {e}")
            return None

    def get_statistics(self, result: PuzzleGenerationResult) -> dict[str, Any]:
        """
        Get detailed statistics from a generation result.

        Args:
            result: Generation result

        Returns:
            Dictionary with detailed statistics
        """
        stats = {
            "success": result.success,
            "status": result.status,
            "word_count": result.word_count,
            "fill_rate": result.fill_rate,
            "iterations": result.iterations,
            "has_error": result.error_message is not None,
        }

        # Add grid statistics if available
        grid = self.get_grid_from_result(result)
        if grid:
            stats.update({
                "grid_size": grid.size,
                "total_cells": grid.size * grid.size,
                "filled_cells": int(grid.size * grid.size * result.fill_rate),
                "words": [word.text for word in grid.words],
                "word_lengths": [len(word.text) for word in grid.words],
                "average_word_length": (
                    sum(len(word.text) for word in grid.words) / len(grid.words)
                    if grid.words else 0
                ),
            })

        return stats

    def retry_generation(
        self,
        request: PuzzleGenerationRequest,
        max_retries: int = 3
    ) -> PuzzleGenerationResult:
        """
        Generate puzzle with automatic retries on failure.

        This method attempts to generate a puzzle multiple times,
        adjusting parameters if needed to improve success rate.

        Args:
            request: Puzzle generation request
            max_retries: Maximum number of retry attempts

        Returns:
            PuzzleGenerationResult from successful attempt or last failure
        """
        logger.info(f"Starting puzzle generation with up to {max_retries} retries")

        last_result = None

        for attempt in range(max_retries):
            logger.info(f"Generation attempt {attempt + 1}/{max_retries}")

            # Validate request
            is_valid, error_msg = self.validate_request(request)
            if not is_valid:
                logger.error(f"Invalid request: {error_msg}")
                return PuzzleGenerationResult(
                    success=False,
                    status="failed",
                    error_message=f"Invalid request: {error_msg}",
                )

            # Generate puzzle
            result = self.generate_puzzle(request)

            # Check if successful
            if result.success:
                logger.info(f"Puzzle generation succeeded on attempt {attempt + 1}")
                return result

            last_result = result

            # Adjust parameters for retry
            if attempt < max_retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed, adjusting parameters for retry"
                )
                # Reduce min_words slightly to increase success chance
                if request.min_words > 4:
                    request.min_words = max(4, request.min_words - 2)
                # Increase max_iterations
                request.max_iterations = min(100, request.max_iterations + 10)

        logger.error(f"All {max_retries} generation attempts failed")
        return last_result or PuzzleGenerationResult(
            success=False,
            status="failed",
            error_message="All retry attempts failed",
        )


# Singleton instance for convenience
_orchestrator_instance: Optional[PuzzleOrchestrator] = None


def get_orchestrator() -> PuzzleOrchestrator:
    """
    Get the singleton orchestrator instance.

    Returns:
        PuzzleOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = PuzzleOrchestrator()
    return _orchestrator_instance


def create_orchestrator(
    planner_agent: Optional[PlannerAgent] = None,
    word_generator_agent: Optional[WordGeneratorAgent] = None,
) -> PuzzleOrchestrator:
    """
    Create a new orchestrator instance with custom agents.

    Args:
        planner_agent: Custom PlannerAgent instance
        word_generator_agent: Custom WordGeneratorAgent instance

    Returns:
        New PuzzleOrchestrator instance
    """
    return PuzzleOrchestrator(
        planner_agent=planner_agent,
        word_generator_agent=word_generator_agent,
    )
