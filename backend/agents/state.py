"""
Agent state management for LangGraph workflow.

This module defines the shared state structure used by all agents in the
crossword puzzle generation workflow. The state is passed between agents
and updated as the workflow progresses.
"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from domain import CrosswordGrid


class PuzzleRequirements(BaseModel):
    """
    Requirements for puzzle generation.

    Attributes:
        topic: Topic for puzzle generation (e.g., "Science", "History")
        grid_size: Size of the grid (NxN)
        min_words: Minimum number of words to place
        max_words: Maximum number of words to place
        difficulty: Difficulty level (easy, medium, hard)
    """
    topic: str = Field(..., description="Topic for puzzle generation")
    grid_size: int = Field(default=8, ge=4, le=20, description="Grid size (NxN)")
    min_words: int = Field(default=8, ge=4, description="Minimum number of words")
    max_words: int = Field(default=15, ge=4, description="Maximum number of words")
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Difficulty level"
    )


class WordCandidate(BaseModel):
    """
    A candidate word for placement on the grid.

    Attributes:
        word: The word text (uppercase)
        clue: Clue text for this word
        priority: Priority score (higher = more important to place)
        category: Category or theme of the word
    """
    word: str = Field(..., description="Word text (uppercase)")
    clue: str = Field(..., description="Clue text")
    priority: float = Field(default=1.0, ge=0.0, description="Priority score")
    category: Optional[str] = Field(default=None, description="Word category/theme")


class PlacementPlan(BaseModel):
    """
    Strategic plan for word placement.

    Attributes:
        word: Word to place
        clue: Clue for the word
        start_row: Starting row position
        start_col: Starting column position
        direction: Direction (across or down)
        priority: Priority for placement
        reasoning: Explanation for this placement choice
    """
    word: str = Field(..., description="Word to place")
    clue: str = Field(..., description="Clue text")
    start_row: int = Field(..., ge=0, description="Starting row")
    start_col: int = Field(..., ge=0, description="Starting column")
    direction: Literal["across", "down"] = Field(..., description="Word direction")
    priority: float = Field(default=1.0, ge=0.0, description="Placement priority")
    reasoning: str = Field(default="", description="Reasoning for placement")


class AgentState(BaseModel):
    """
    Shared state for the crossword puzzle generation workflow.

    This state is passed between agents and updated as the workflow progresses.
    Each agent reads from and writes to this state to coordinate puzzle generation.

    Attributes:
        requirements: Puzzle generation requirements
        grid_state: Current grid state (serialized)
        word_candidates: List of candidate words for placement
        placement_plan: Ordered list of planned word placements
        placed_words: List of successfully placed words
        failed_placements: List of placements that failed
        iteration: Current iteration number
        max_iterations: Maximum iterations allowed
        status: Current workflow status
        error_message: Error message if workflow failed
        metadata: Additional metadata for tracking
    """

    # Input requirements
    requirements: PuzzleRequirements = Field(
        ...,
        description="Puzzle generation requirements"
    )

    # Grid state (serialized for LangGraph compatibility)
    grid_state: Optional[dict[str, Any]] = Field(
        default=None,
        description="Serialized grid state"
    )

    # Word candidates and planning
    word_candidates: list[WordCandidate] = Field(
        default_factory=list,
        description="Candidate words for placement"
    )

    placement_plan: list[PlacementPlan] = Field(
        default_factory=list,
        description="Ordered list of planned placements"
    )

    # Execution tracking
    placed_words: list[str] = Field(
        default_factory=list,
        description="Successfully placed words"
    )

    failed_placements: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Failed placement attempts with reasons"
    )

    # Iteration control
    iteration: int = Field(
        default=0,
        ge=0,
        description="Current iteration number"
    )

    max_iterations: int = Field(
        default=50,
        ge=1,
        description="Maximum iterations allowed"
    )

    # Status tracking
    status: Literal["initializing", "planning", "executing", "completed", "failed"] = Field(
        default="initializing",
        description="Current workflow status"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error message if workflow failed"
    )

    # Metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for tracking"
    )

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    def get_grid(self) -> Optional[CrosswordGrid]:
        """
        Deserialize and return the current grid.

        Returns:
            CrosswordGrid instance or None if not initialized
        """
        if self.grid_state is None:
            return None
        return CrosswordGrid.from_dict(self.grid_state)

    def set_grid(self, grid: CrosswordGrid) -> None:
        """
        Serialize and store the grid state.

        Args:
            grid: CrosswordGrid instance to serialize
        """
        self.grid_state = grid.to_dict()

    def add_placed_word(self, word: str) -> None:
        """
        Add a word to the placed words list.

        Args:
            word: Word that was successfully placed
        """
        if word not in self.placed_words:
            self.placed_words.append(word)

    def add_failed_placement(
        self,
        word: str,
        reason: str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Record a failed placement attempt.

        Args:
            word: Word that failed to place
            reason: Reason for failure
            details: Additional details about the failure
        """
        failure = {
            "word": word,
            "reason": reason,
            "iteration": self.iteration,
        }
        if details:
            failure["details"] = details
        self.failed_placements.append(failure)

    def increment_iteration(self) -> None:
        """Increment the iteration counter."""
        self.iteration += 1

    def is_max_iterations_reached(self) -> bool:
        """
        Check if maximum iterations have been reached.

        Returns:
            True if max iterations reached, False otherwise
        """
        return self.iteration >= self.max_iterations

    def get_fill_rate(self) -> float:
        """
        Get the current grid fill rate.

        Returns:
            Fill rate as a float between 0.0 and 1.0
        """
        grid = self.get_grid()
        if grid is None:
            return 0.0
        return grid.get_fill_rate()

    def get_word_count(self) -> int:
        """
        Get the number of words currently placed on the grid.

        Returns:
            Number of placed words
        """
        grid = self.get_grid()
        if grid is None:
            return 0
        return len(grid.words)

    def is_requirements_met(self) -> bool:
        """
        Check if puzzle requirements are met.

        Returns:
            True if requirements are satisfied, False otherwise
        """
        word_count = self.get_word_count()
        return word_count >= self.requirements.min_words

    def mark_completed(self) -> None:
        """Mark the workflow as completed."""
        self.status = "completed"

    def mark_failed(self, error_message: str) -> None:
        """
        Mark the workflow as failed.

        Args:
            error_message: Error message describing the failure
        """
        self.status = "failed"
        self.error_message = error_message

    def to_dict(self) -> dict[str, Any]:
        """
        Convert state to dictionary for serialization.

        Returns:
            Dictionary representation of state
        """
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentState":
        """
        Create state from dictionary.

        Args:
            data: Dictionary representation of state

        Returns:
            AgentState instance
        """
        return cls(**data)
