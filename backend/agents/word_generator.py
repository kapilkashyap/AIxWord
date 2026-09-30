"""
WordGeneratorAgent implementation for crossword puzzle generation.

This module implements the WordGeneratorAgent, which is responsible for executing
the placement plans created by the PlannerAgent. The agent generates words that
fit specific patterns, validates placements, and places words on the grid.
"""

import json
import logging
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError

from domain import CrosswordGrid, Direction, WordPlacement
from domain.pattern import Pattern
from domain.validator import WordValidator
from llm import LLMClient, get_llm_client

from .state import AgentState, PlacementPlan
from .word_generator_prompts import WordGeneratorPrompts

logger = logging.getLogger(__name__)


class WordGenerationResult(BaseModel):
    """
    Result from word generation attempt.

    Attributes:
        word: Generated word (uppercase)
        clue: Clue for the word
        confidence: Confidence score (0.0 to 1.0)
        reasoning: Explanation for the word choice
        alternatives: Alternative word suggestions
    """
    word: str = Field(..., description="Generated word (uppercase)")
    clue: str = Field(..., description="Clue for the word")
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )
    reasoning: str = Field(default="", description="Reasoning for word choice")
    alternatives: list[str] = Field(
        default_factory=list,
        description="Alternative word suggestions"
    )


class WordGeneratorAction(BaseModel):
    """
    Action result from the WordGeneratorAgent.

    Attributes:
        success: Whether word generation was successful
        word_result: Generated word result (if successful)
        error_message: Error message (if failed)
        should_retry: Whether to retry with different parameters
    """
    success: bool = Field(..., description="Whether generation was successful")
    word_result: Optional[WordGenerationResult] = Field(
        default=None,
        description="Generated word result"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )
    should_retry: bool = Field(
        default=False,
        description="Whether to retry generation"
    )


class WordGeneratorAgent:
    """
    Word generation and placement execution agent.

    The WordGeneratorAgent is responsible for:
    1. Extracting patterns from the grid for word placement
    2. Generating words that fit specific patterns using LLM
    3. Validating word placements
    4. Placing words on the grid
    5. Handling placement failures and retries

    The agent works in coordination with the PlannerAgent, executing the
    placement plans created by the planner.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the WordGeneratorAgent.

        Args:
            llm_client: LLM client for API calls (uses default if not provided)
        """
        self.llm_client = llm_client or get_llm_client()
        self.prompts = WordGeneratorPrompts()
        logger.info("WordGeneratorAgent initialized")

    def extract_pattern(
        self,
        grid: CrosswordGrid,
        placement_plan: PlacementPlan
    ) -> Pattern:
        """
        Extract the current pattern from the grid for a placement position.

        This method determines what letters are already filled in the positions
        where the word would be placed, creating a pattern like "A__LE" for
        a 5-letter word where positions 0 and 3-4 are filled.

        Args:
            grid: Current crossword grid
            placement_plan: Planned placement position

        Returns:
            Pattern object representing the current grid state
        """
        pattern_chars = []

        # Calculate positions based on direction
        for i in range(len(placement_plan.word)):
            if placement_plan.direction == "across":
                row = placement_plan.start_row
                col = placement_plan.start_col + i
            else:  # down
                row = placement_plan.start_row + i
                col = placement_plan.start_col

            # Check if position is valid
            if not grid.is_valid_position(row, col):
                pattern_chars.append("_")
                continue

            # Get cell value
            cell = grid.get_cell(row, col)
            if cell.value is not None:
                pattern_chars.append(cell.value)
            else:
                pattern_chars.append("_")

        pattern_str = "".join(pattern_chars)
        logger.debug(f"Extracted pattern: {pattern_str} for position "
                    f"({placement_plan.start_row}, {placement_plan.start_col}) "
                    f"{placement_plan.direction}")

        return Pattern(pattern_str)

    def get_intersecting_constraints(
        self,
        grid: CrosswordGrid,
        placement_plan: PlacementPlan
    ) -> list[dict[str, Any]]:
        """
        Get constraints from intersecting words.

        This method identifies which positions in the planned placement
        intersect with existing words and what letters are required at
        those positions.

        Args:
            grid: Current crossword grid
            placement_plan: Planned placement position

        Returns:
            List of constraint dictionaries with position and letter info
        """
        constraints = []
        word_length = len(placement_plan.word)

        for i in range(word_length):
            if placement_plan.direction == "across":
                row = placement_plan.start_row
                col = placement_plan.start_col + i
            else:  # down
                row = placement_plan.start_row + i
                col = placement_plan.start_col

            if not grid.is_valid_position(row, col):
                continue

            cell = grid.get_cell(row, col)
            if cell.value is not None:
                # Find which word this letter belongs to
                intersecting_direction = (
                    Direction.DOWN if placement_plan.direction == "across"
                    else Direction.ACROSS
                )
                intersecting_word = grid.get_word_at(row, col, intersecting_direction)

                if intersecting_word:
                    constraints.append({
                        "position": i,
                        "letter": cell.value,
                        "intersecting_word": intersecting_word.text,
                        "row": row,
                        "col": col,
                    })

        return constraints

    def generate_word(
        self,
        state: AgentState,
        placement_plan: PlacementPlan,
        pattern: Pattern
    ) -> WordGeneratorAction:
        """
        Generate a word that fits the given pattern and placement plan.

        This method uses the LLM to generate a word that:
        - Matches the required pattern
        - Fits the topic and difficulty
        - Has an appropriate clue
        - Respects intersecting word constraints

        Args:
            state: Current agent state
            placement_plan: Planned placement position
            pattern: Pattern to match

        Returns:
            WordGeneratorAction with generation result
        """
        logger.info(
            f"Generating word for pattern '{pattern}' at "
            f"({placement_plan.start_row}, {placement_plan.start_col}) "
            f"{placement_plan.direction}"
        )

        # Get grid and constraints
        grid = state.get_grid()
        if grid is None:
            grid = CrosswordGrid(size=state.requirements.grid_size)
            state.set_grid(grid)

        constraints = self.get_intersecting_constraints(grid, placement_plan)

        # Build prompt messages
        system_prompt = self.prompts.system_prompt()
        user_prompt = self.prompts.user_prompt(
            topic=state.requirements.topic,
            pattern=pattern,
            difficulty=state.requirements.difficulty,
            direction=placement_plan.direction,
            constraints=constraints,
            placed_words=state.placed_words,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Call LLM
        try:
            response = self.llm_client.get_json_response(
                messages=messages,
                temperature=0.8,  # Higher temperature for creativity
                max_tokens=1000,
            )

            logger.debug(f"LLM response received with keys: {list(response.keys())}")

            # Parse and validate response
            word_result = self._parse_llm_response(response, pattern)

            if word_result is None:
                return WordGeneratorAction(
                    success=False,
                    error_message="Failed to parse LLM response",
                    should_retry=True,
                )

            logger.info(
                f"Generated word: {word_result.word} "
                f"(confidence: {word_result.confidence:.2f})"
            )

            return WordGeneratorAction(
                success=True,
                word_result=word_result,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return WordGeneratorAction(
                success=False,
                error_message=f"JSON parsing error: {str(e)}",
                should_retry=True,
            )
        except ValidationError as e:
            logger.error(f"LLM response validation failed: {e}")
            return WordGeneratorAction(
                success=False,
                error_message=f"Validation error: {str(e)}",
                should_retry=True,
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}", exc_info=True)
            return WordGeneratorAction(
                success=False,
                error_message=f"LLM error: {str(e)}",
                should_retry=False,
            )

    def _parse_llm_response(
        self,
        response: dict[str, Any],
        pattern: Pattern
    ) -> Optional[WordGenerationResult]:
        """
        Parse and validate LLM response into WordGenerationResult.

        Args:
            response: Raw JSON response from LLM
            pattern: Expected pattern for validation

        Returns:
            Validated WordGenerationResult or None if invalid
        """
        try:
            # Extract required fields
            word = response.get("word", "").upper()
            clue = response.get("clue", "")

            if not word or not clue:
                logger.warning("Missing word or clue in LLM response")
                return None

            # Validate word matches pattern
            if not pattern.matches(word):
                logger.warning(
                    f"Generated word '{word}' does not match pattern '{pattern}'"
                )
                return None

            # Create result
            result = WordGenerationResult(
                word=word,
                clue=clue,
                confidence=response.get("confidence", 0.8),
                reasoning=response.get("reasoning", ""),
                alternatives=response.get("alternatives", []),
            )

            return result

        except (KeyError, ValidationError) as e:
            logger.error(f"Failed to parse word generation result: {e}")
            return None

    def execute_placement(
        self,
        state: AgentState,
        placement_plan: PlacementPlan
    ) -> bool:
        """
        Execute a word placement on the grid.

        This method:
        1. Extracts the pattern from the grid
        2. Generates a word that fits the pattern
        3. Validates the placement
        4. Places the word on the grid
        5. Updates the state

        Args:
            state: Current agent state
            placement_plan: Placement plan to execute

        Returns:
            True if placement was successful, False otherwise
        """
        logger.info(
            f"Executing placement: {placement_plan.word} at "
            f"({placement_plan.start_row}, {placement_plan.start_col}) "
            f"{placement_plan.direction}"
        )

        # Get or create grid
        grid = state.get_grid()
        if grid is None:
            grid = CrosswordGrid(size=state.requirements.grid_size)
            state.set_grid(grid)

        # Extract pattern
        pattern = self.extract_pattern(grid, placement_plan)

        # Check if pattern is already complete (word already placed)
        if pattern.is_complete:
            logger.info(f"Pattern already complete: {pattern}")
            # Verify it matches the planned word
            if pattern.pattern == placement_plan.word.upper():
                logger.info("Word already placed correctly")
                return True
            else:
                logger.warning(
                    f"Pattern mismatch: expected {placement_plan.word}, "
                    f"got {pattern.pattern}"
                )
                return False

        # Generate word for pattern
        generation_result = self.generate_word(state, placement_plan, pattern)

        if not generation_result.success:
            logger.warning(
                f"Word generation failed: {generation_result.error_message}"
            )
            state.add_failed_placement(
                word=placement_plan.word,
                reason=generation_result.error_message or "Generation failed",
                details={
                    "pattern": str(pattern),
                    "position": (placement_plan.start_row, placement_plan.start_col),
                    "direction": placement_plan.direction,
                },
            )
            return False

        # Get generated word
        word_result = generation_result.word_result
        if word_result is None:
            logger.error("Word result is None despite success flag")
            return False

        # Create word placement
        direction = (
            Direction.ACROSS if placement_plan.direction == "across"
            else Direction.DOWN
        )

        word_placement = WordPlacement(
            word=word_result.word,
            start_row=placement_plan.start_row,
            start_col=placement_plan.start_col,
            direction=direction,
            clue=word_result.clue,
            number=1,  # Temporary number, will be reassigned by grid.assign_numbers()
        )

        # Validate placement
        validation_result = WordValidator.validate_placement(grid, word_placement)

        if not validation_result.is_valid:
            logger.warning(
                f"Placement validation failed: {validation_result.errors}"
            )
            state.add_failed_placement(
                word=word_result.word,
                reason="Validation failed",
                details={
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                },
            )
            return False

        # Place word on grid
        success = grid.place_word(word_placement)

        if not success:
            logger.warning(f"Failed to place word {word_result.word} on grid")
            state.add_failed_placement(
                word=word_result.word,
                reason="Grid placement failed",
                details={
                    "position": (placement_plan.start_row, placement_plan.start_col),
                    "direction": placement_plan.direction,
                },
            )
            return False

        # Update state
        state.add_placed_word(word_result.word)
        state.set_grid(grid)

        logger.info(
            f"Successfully placed word: {word_result.word} "
            f"(fill rate: {grid.get_fill_rate():.1%})"
        )

        return True

    def execute_placement_plan(
        self,
        state: AgentState,
        max_placements: int = 3
    ) -> int:
        """
        Execute multiple placements from the state's placement plan.

        This method processes the placement plan in order, attempting to
        place each word. It stops after max_placements successful placements
        or when the plan is exhausted.

        Args:
            state: Current agent state with placement plan
            max_placements: Maximum number of placements to attempt

        Returns:
            Number of successful placements
        """
        if not state.placement_plan:
            logger.warning("No placement plan to execute")
            return 0

        successful_placements = 0

        # Process placement plan
        for i, placement_plan in enumerate(state.placement_plan):
            if successful_placements >= max_placements:
                logger.info(
                    f"Reached max placements limit ({max_placements}), stopping"
                )
                break

            logger.info(
                f"Processing placement {i + 1}/{len(state.placement_plan)}: "
                f"{placement_plan.word}"
            )

            # Execute placement
            success = self.execute_placement(state, placement_plan)

            if success:
                successful_placements += 1
            else:
                logger.warning(
                    f"Placement failed for {placement_plan.word}, continuing..."
                )

        logger.info(
            f"Executed {successful_placements} successful placements "
            f"out of {len(state.placement_plan)} planned"
        )

        return successful_placements

    def should_continue(self, state: AgentState) -> bool:
        """
        Determine if word generation should continue.

        This checks:
        - Whether requirements are met
        - Whether max iterations reached
        - Whether there are more placements to execute

        Args:
            state: Current agent state

        Returns:
            True if generation should continue, False otherwise
        """
        # Check requirements
        if state.is_requirements_met():
            logger.info("Requirements met, stopping generation")
            return False

        # Check iterations
        if state.is_max_iterations_reached():
            logger.warning("Max iterations reached, stopping generation")
            return False

        # Check if we have a placement plan
        if not state.placement_plan:
            logger.info("No placement plan available, need planning phase")
            return True

        return True
