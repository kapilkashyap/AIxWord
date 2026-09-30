"""
PlannerAgent implementation for crossword puzzle generation.

This module implements the PlannerAgent, which is responsible for strategic
planning of word placements in the crossword puzzle. The agent analyzes the
current grid state, generates word candidates based on the topic, and creates
a strategic placement plan.
"""

import json
import logging
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError

from domain import CrosswordGrid
from llm import LLMClient, get_llm_client

from .planner_prompts import PlannerPrompts
from .state import AgentState, PlacementPlan, WordCandidate

logger = logging.getLogger(__name__)


class PlannerAction(BaseModel):
    """
    Action decision from the PlannerAgent.

    Attributes:
        action: Type of action (ADD_WORD or STOP)
        reasoning: Explanation for the decision
        word_candidates: List of word candidates to consider
        placement_plan: Ordered list of planned placements
        stop_reason: Reason for stopping (if action is STOP)
    """
    action: str = Field(..., description="Action type: ADD_WORD or STOP")
    reasoning: str = Field(..., description="Reasoning for the decision")
    word_candidates: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of word candidates"
    )
    placement_plan: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Ordered list of planned placements"
    )
    stop_reason: Optional[str] = Field(
        default=None,
        description="Reason for stopping (if applicable)"
    )


class PlannerAgent:
    """
    Strategic planning agent for crossword puzzle generation.

    The PlannerAgent is responsible for:
    1. Analyzing the current grid state
    2. Generating word candidates based on topic and requirements
    3. Creating strategic placement plans
    4. Deciding when to stop puzzle generation

    The agent uses an LLM to make intelligent decisions about word selection
    and placement strategy.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the PlannerAgent.

        Args:
            llm_client: LLM client for API calls (uses default if not provided)
        """
        self.llm_client = llm_client or get_llm_client()
        self.prompts = PlannerPrompts()
        logger.info("PlannerAgent initialized")

    def analyze_grid_state(self, state: AgentState) -> dict[str, Any]:
        """
        Analyze the current grid state and extract relevant information.

        Args:
            state: Current agent state

        Returns:
            Dictionary with grid analysis information
        """
        grid = state.get_grid()

        if grid is None:
            return {
                "grid_size": state.requirements.grid_size,
                "placed_words": [],
                "fill_rate": 0.0,
                "available_spaces": state.requirements.grid_size ** 2,
                "iteration": state.iteration,
            }

        analysis = {
            "grid_size": grid.size,
            "placed_words": [word.text for word in grid.words],
            "fill_rate": grid.get_fill_rate(),
            "word_count": len(grid.words),
            "iteration": state.iteration,
            "available_spaces": self._count_available_spaces(grid),
            "intersections": self._analyze_intersections(grid),
        }

        logger.debug(f"Grid analysis: {analysis}")
        return analysis

    def _count_available_spaces(self, grid: CrosswordGrid) -> int:
        """
        Count the number of available spaces for new words.

        Args:
            grid: Current crossword grid

        Returns:
            Number of empty cells
        """
        count = 0
        for row in range(grid.size):
            for col in range(grid.size):
                cell = grid.get_cell(row, col)
                if cell.is_empty:
                    count += 1
        return count

    def _analyze_intersections(self, grid: CrosswordGrid) -> dict[str, Any]:
        """
        Analyze word intersections on the grid.

        Args:
            grid: Current crossword grid

        Returns:
            Dictionary with intersection analysis
        """
        intersections = []
        words = grid.words

        for i, word1 in enumerate(words):
            for word2 in words[i + 1:]:
                intersection = word1.intersects_with(word2)
                if intersection:
                    intersections.append({
                        "word1": word1.text,
                        "word2": word2.text,
                        "position": intersection,
                    })

        return {
            "count": len(intersections),
            "details": intersections,
        }

    def generate_placement_plan(self, state: AgentState) -> PlannerAction:
        """
        Generate a strategic placement plan for the next words.

        This method uses the LLM to analyze the current state and generate
        a plan for placing new words on the grid.

        Args:
            state: Current agent state

        Returns:
            PlannerAction with word candidates and placement plan

        Raises:
            Exception: If LLM call fails or response is invalid
        """
        logger.info(
            f"Generating placement plan (iteration {state.iteration + 1})"
        )

        # Analyze current grid state
        grid_analysis = self.analyze_grid_state(state)

        # Check if we should stop
        if self._should_stop_planning(state, grid_analysis):
            return PlannerAction(
                action="STOP",
                reasoning="Requirements met or maximum iterations reached",
                stop_reason=self._get_stop_reason(state, grid_analysis),
            )

        # Build prompt messages
        system_prompt = self.prompts.system_prompt()
        user_prompt = self.prompts.user_prompt(
            topic=state.requirements.topic,
            grid_size=state.requirements.grid_size,
            min_words=state.requirements.min_words,
            max_words=state.requirements.max_words,
            difficulty=state.requirements.difficulty,
            grid_analysis=grid_analysis,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Call LLM
        try:
            logger.info("Calling OpenAI API for placement plan...")
            response = self.llm_client.get_json_response(
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )

            # Log response (avoid JSON serialization of complex objects)
            logger.debug(f"LLM response received with keys: {list(response.keys())}")

            # Parse and validate response
            action = self._parse_llm_response(response)

            logger.info(
                f"Generated plan with {len(action.word_candidates)} candidates "
                f"and {len(action.placement_plan)} placements"
            )

            return action

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except ValidationError as e:
            logger.error(f"LLM response validation failed: {e}")
            raise
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"LLM call failed: {type(e).__name__}: {str(e)}", exc_info=True)
            
            # Check for common OpenAI/network issues
            if "401" in error_msg or "unauthorized" in error_msg:
                logger.error("❌ OpenAI API key is invalid or missing!")
            elif "403" in error_msg or "forbidden" in error_msg:
                logger.error("❌ OpenAI API key doesn't have access to this model!")
            elif "timeout" in error_msg or "connection" in error_msg:
                logger.error("❌ Network/firewall blocking OpenAI API (check Zscaler/proxy)!")
            elif "ssl" in error_msg or "certificate" in error_msg:
                logger.error("❌ SSL/TLS certificate issue (common with corporate proxies)!")
            
            raise

    def _parse_llm_response(self, response: dict[str, Any]) -> PlannerAction:
        """
        Parse and validate LLM response into PlannerAction.

        Args:
            response: Raw JSON response from LLM

        Returns:
            Validated PlannerAction instance

        Raises:
            ValidationError: If response doesn't match expected schema
        """
        # Log the raw response for debugging
        logger.debug(f"Raw LLM response type: {type(response)}")
        logger.debug(f"Raw LLM response: {response}")
        
        # Check if response is actually a dict
        if not isinstance(response, dict):
            logger.error(f"LLM response is not a dict! Type: {type(response)}, Value: {response}")
            raise ValueError(f"Expected dict response, got {type(response)}")
        
        # Ensure action field exists
        if "action" not in response:
            # If no explicit action, assume ADD_WORD if we have candidates
            if response.get("word_candidates") or response.get("placement_plan"):
                response["action"] = "ADD_WORD"
            else:
                response["action"] = "STOP"

        # Ensure reasoning exists
        if "reasoning" not in response:
            response["reasoning"] = "No reasoning provided"
        
        # Ensure word_candidates is a list
        if "word_candidates" in response and not isinstance(response["word_candidates"], list):
            logger.warning(f"word_candidates is not a list: {type(response['word_candidates'])}")
            response["word_candidates"] = []
        
        # Ensure placement_plan is a list
        if "placement_plan" in response and not isinstance(response["placement_plan"], list):
            logger.warning(f"placement_plan is not a list: {type(response['placement_plan'])}")
            response["placement_plan"] = []

        # Validate and create PlannerAction
        try:
            return PlannerAction(**response)
        except Exception as e:
            logger.error(f"Failed to create PlannerAction: {e}")
            logger.error(f"Response data: {response}")
            raise

    def _should_stop_planning(
        self,
        state: AgentState,
        grid_analysis: dict[str, Any]
    ) -> bool:
        """
        Determine if planning should stop.

        Args:
            state: Current agent state
            grid_analysis: Grid analysis information

        Returns:
            True if planning should stop, False otherwise
        """
        # Check if requirements are met
        if state.is_requirements_met():
            logger.info("Requirements met, stopping planning")
            return True

        # Check if max iterations reached
        if state.is_max_iterations_reached():
            logger.warning("Max iterations reached, stopping planning")
            return True

        # Check if grid is nearly full
        fill_rate = grid_analysis.get("fill_rate", 0.0)
        if fill_rate >= 0.9:
            logger.info(f"Grid nearly full ({fill_rate:.1%}), stopping planning")
            return True

        return False

    def _get_stop_reason(
        self,
        state: AgentState,
        grid_analysis: dict[str, Any]
    ) -> str:
        """
        Get the reason for stopping planning.

        Args:
            state: Current agent state
            grid_analysis: Grid analysis information

        Returns:
            Human-readable stop reason
        """
        if state.is_requirements_met():
            return (
                f"Requirements met: {state.get_word_count()} words placed "
                f"(min: {state.requirements.min_words})"
            )

        if state.is_max_iterations_reached():
            return (
                f"Maximum iterations ({state.max_iterations}) reached with "
                f"{state.get_word_count()} words placed"
            )

        fill_rate = grid_analysis.get("fill_rate", 0.0)
        if fill_rate >= 0.9:
            return f"Grid nearly full ({fill_rate:.1%})"

        return "Unknown reason"

    def select_next_word(
        self,
        state: AgentState,
        action: PlannerAction
    ) -> Optional[PlacementPlan]:
        """
        Select the next word to place from the placement plan.

        Args:
            state: Current agent state
            action: PlannerAction with placement plan

        Returns:
            PlacementPlan for the next word, or None if no valid placements
        """
        if not action.placement_plan:
            logger.warning("No placement plan available")
            return None

        # Get the first placement from the plan
        placement_dict = action.placement_plan[0]

        try:
            # Validate and create PlacementPlan
            placement = PlacementPlan(
                word=placement_dict["word"],
                clue=placement_dict["clue"],
                start_row=placement_dict["start_row"],
                start_col=placement_dict["start_col"],
                direction=placement_dict["direction"],
                priority=placement_dict.get("priority", 1.0),
                reasoning=placement_dict.get("reasoning", ""),
            )

            logger.info(
                f"Selected word: {placement.word} at "
                f"({placement.start_row}, {placement.start_col}) "
                f"{placement.direction}"
            )

            return placement

        except (KeyError, ValidationError) as e:
            logger.error(f"Failed to parse placement plan: {e}")
            return None

    def update_state_with_candidates(
        self,
        state: AgentState,
        action: PlannerAction
    ) -> None:
        """
        Update agent state with word candidates from the plan.

        Args:
            state: Agent state to update
            action: PlannerAction with word candidates
        """
        # Clear existing candidates
        state.word_candidates.clear()

        # Add new candidates
        for candidate_dict in action.word_candidates:
            try:
                candidate = WordCandidate(
                    word=candidate_dict["word"],
                    clue=candidate_dict["clue"],
                    priority=candidate_dict.get("priority", 1.0),
                    category=candidate_dict.get("category"),
                )
                state.word_candidates.append(candidate)
            except (KeyError, ValidationError) as e:
                logger.warning(f"Failed to parse word candidate: {e}")
                continue

        logger.info(f"Updated state with {len(state.word_candidates)} candidates")

    def should_stop(self, state: AgentState) -> bool:
        """
        Determine if the workflow should stop.

        This is a high-level check that considers multiple factors:
        - Requirements met
        - Maximum iterations reached
        - No more valid placements possible

        Args:
            state: Current agent state

        Returns:
            True if workflow should stop, False otherwise
        """
        # Check requirements
        if state.is_requirements_met():
            return True

        # Check iterations
        if state.is_max_iterations_reached():
            return True

        # Check if we have too many consecutive failures
        # Increased threshold since we now filter invalid placements early
        recent_failures = state.failed_placements[-10:]
        if len(recent_failures) >= 10:
            logger.warning("Too many consecutive failures, stopping")
            return True

        return False
