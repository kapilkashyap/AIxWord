"""
LangGraph workflow orchestration for crossword puzzle generation.

This module defines the workflow graph that coordinates the PlannerAgent and
WordGeneratorAgent to generate crossword puzzles. The workflow uses LangGraph's
StateGraph to manage state transitions and agent coordination.
"""

import logging
from typing import Any, Literal, Optional

from langgraph.graph import END, StateGraph

from domain import CrosswordGrid

from .planner import PlannerAgent
from .state import AgentState, PuzzleRequirements
from .word_generator import WordGeneratorAgent

logger = logging.getLogger(__name__)


class CrosswordWorkflow:
    """
    LangGraph workflow for crossword puzzle generation.

    This workflow coordinates two agents:
    1. PlannerAgent: Creates strategic plan for word placement
    2. WordGeneratorAgent: Executes the plan by placing words on grid

    The workflow iterates between planning and execution until requirements
    are met or maximum iterations are reached.
    """

    def __init__(
        self,
        planner_agent: Optional[PlannerAgent] = None,
        word_generator_agent: Optional[WordGeneratorAgent] = None,
    ) -> None:
        """
        Initialize the workflow graph.

        Args:
            planner_agent: PlannerAgent instance (creates default if not provided)
            word_generator_agent: WordGeneratorAgent instance (creates default if not provided)
        """
        self.planner_agent = planner_agent or PlannerAgent()
        self.word_generator_agent = word_generator_agent or WordGeneratorAgent()
        self.graph = self._build_graph()
        logger.info("CrosswordWorkflow initialized with PlannerAgent and WordGeneratorAgent")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph StateGraph for puzzle generation.

        The graph structure:
        1. initialize -> planner
        2. planner -> executor
        3. executor -> should_continue
        4. should_continue -> planner (if continue) or END (if done)

        Returns:
            Compiled StateGraph instance
        """
        # Create the graph with AgentState as the state schema
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)

        # Set entry point
        workflow.set_entry_point("initialize")

        # Add edges
        workflow.add_edge("initialize", "planner")
        workflow.add_edge("planner", "executor")

        # Add conditional edge from executor
        workflow.add_conditional_edges(
            "executor",
            self._should_continue,
            {
                "continue": "planner",
                "end": END,
            }
        )

        # Compile the graph
        return workflow.compile()

    def _initialize_node(self, state: AgentState) -> dict[str, Any]:
        """
        Initialize the workflow state.

        This node:
        1. Creates an empty grid
        2. Sets initial status
        3. Prepares for planning phase

        Args:
            state: Current agent state

        Returns:
            Dictionary with state updates
        """
        logger.info(
            f"Initializing workflow for topic: {state.requirements.topic}, "
            f"grid size: {state.requirements.grid_size}x{state.requirements.grid_size}"
        )

        # Create empty grid
        grid = CrosswordGrid(size=state.requirements.grid_size)

        # Update state
        updates = {
            "grid_state": grid.to_dict(),
            "status": "planning",
            "iteration": 0,
            "metadata": {
                "initialized_at": "workflow_start",
                "grid_size": state.requirements.grid_size,
                "topic": state.requirements.topic,
            }
        }

        logger.info("Workflow initialized successfully")
        return updates

    def _planner_node(self, state: AgentState) -> dict[str, Any]:
        """
        Planner agent node - generates strategic placement plan.

        This node:
        1. Analyzes current grid state
        2. Generates word candidates based on topic
        3. Creates strategic placement plan
        4. Prioritizes words for placement

        Args:
            state: Current agent state

        Returns:
            Dictionary with state updates
        """
        # Handle dict input from LangGraph
        if isinstance(state, dict):
            try:
                state = AgentState(**state)
            except Exception as e:
                logger.error(f"Failed to convert dict to AgentState: {e}")
                raise

        logger.info(f"Planning iteration {state.iteration + 1}")

        try:
            # Generate placement plan using PlannerAgent
            action = self.planner_agent.generate_placement_plan(state)

            # Check if planner decided to stop
            if action.action == "STOP":
                logger.info(f"Planner decided to stop: {action.stop_reason}")
                updates = {
                    "status": "completed",
                    "metadata": {
                        **state.metadata,
                        f"planning_iteration_{state.iteration}": "stopped",
                        "stop_reason": action.stop_reason,
                    }
                }
                return updates

            # Update state with word candidates
            self.planner_agent.update_state_with_candidates(state, action)

            # Convert placement plan to state format with bounds validation
            placement_plan = []
            grid_size = state.requirements.grid_size
            
            for plan_dict in action.placement_plan:
                try:
                    from .state import PlacementPlan
                    
                    # Extract placement details
                    word = plan_dict["word"]
                    start_row = plan_dict["start_row"]
                    start_col = plan_dict["start_col"]
                    direction = plan_dict["direction"]
                    word_length = len(word)
                    
                    # Validate grid bounds BEFORE creating PlacementPlan
                    is_valid = True
                    reason = ""
                    
                    if direction == "across":
                        if start_col + word_length > grid_size:
                            is_valid = False
                            reason = f"ACROSS word '{word}' at col {start_col} with length {word_length} exceeds grid size {grid_size} ({start_col}+{word_length}={start_col+word_length} > {grid_size})"
                    elif direction == "down":
                        if start_row + word_length > grid_size:
                            is_valid = False
                            reason = f"DOWN word '{word}' at row {start_row} with length {word_length} exceeds grid size {grid_size} ({start_row}+{word_length}={start_row+word_length} > {grid_size})"
                    
                    # Also validate start positions are within bounds
                    if start_row < 0 or start_row >= grid_size:
                        is_valid = False
                        reason = f"start_row {start_row} is out of bounds (must be 0-{grid_size-1})"
                    if start_col < 0 or start_col >= grid_size:
                        is_valid = False
                        reason = f"start_col {start_col} is out of bounds (must be 0-{grid_size-1})"
                    
                    if not is_valid:
                        logger.warning(f"Skipping invalid placement: {reason}")
                        # Record this as a failed placement
                        state.add_failed_placement(
                            word=word,
                            reason="Grid bounds validation failed",
                            details={"validation_error": reason}
                        )
                        continue
                    
                    plan = PlacementPlan(
                        word=word,
                        clue=plan_dict["clue"],
                        start_row=start_row,
                        start_col=start_col,
                        direction=direction,
                        priority=plan_dict.get("priority", 1.0),
                        reasoning=plan_dict.get("reasoning", ""),
                    )
                    placement_plan.append(plan)
                    logger.debug(f"✓ Valid placement: {word} at ({start_row},{start_col}) {direction}")
                    
                except (KeyError, Exception) as e:
                    logger.warning(f"Failed to parse placement plan item: {e}")
                    continue

            # Update state
            updates = {
                "status": "planning",
                "placement_plan": placement_plan,
                "word_candidates": state.word_candidates,
                "metadata": {
                    **state.metadata,
                    f"planning_iteration_{state.iteration}": {
                        "candidates_count": len(state.word_candidates),
                        "placements_count": len(placement_plan),
                        "action": action.action,
                    }
                }
            }

            logger.info(
                f"Planning completed: {len(state.word_candidates)} candidates, "
                f"{len(placement_plan)} placements planned"
            )
            return updates

        except Exception as e:
            logger.error(f"Planning failed: {e}", exc_info=True)
            # Return error state but allow workflow to continue
            return {
                "status": "planning",
                "metadata": {
                    **state.metadata,
                    f"planning_iteration_{state.iteration}": f"error: {str(e)}",
                }
            }

    def _executor_node(self, state: AgentState) -> dict[str, Any]:
        """
        Executor agent node - executes placement plan.

        This node:
        1. Executes placement plan from planner
        2. Places words on grid with validation
        3. Tracks successful and failed placements
        4. Updates grid state

        Args:
            state: Current agent state

        Returns:
            Dictionary with state updates
        """
        logger.info(f"Executing iteration {state.iteration + 1}")

        # Increment iteration
        new_iteration = state.iteration + 1

        try:
            # Execute placement plan using WordGeneratorAgent
            successful_placements = self.word_generator_agent.execute_placement_plan(
                state,
                max_placements=5  # Limit placements per iteration
            )

            # Get updated grid state
            grid = state.get_grid()
            grid_state = grid.to_dict() if grid else None

            # Determine status based on iteration and requirements
            status = "executing"
            
            # Check if requirements are met after this execution
            if state.is_requirements_met():
                status = "completed"
                logger.info(f"Requirements met after iteration {new_iteration}")
            # Check if max iterations will be reached after this iteration
            elif new_iteration >= state.max_iterations:
                status = "failed"
                logger.warning(
                    f"Max iterations ({state.max_iterations}) reached. "
                    f"Only {state.get_word_count()} words placed "
                    f"(min: {state.requirements.min_words})"
                )

            # Update state
            updates = {
                "status": status,
                "iteration": new_iteration,
                "grid_state": grid_state,
                "placed_words": state.placed_words,
                "failed_placements": state.failed_placements,
                "metadata": {
                    **state.metadata,
                    f"execution_iteration_{new_iteration}": {
                        "successful_placements": successful_placements,
                        "total_words": len(state.placed_words),
                        "total_failures": len(state.failed_placements),
                    }
                }
            }

            logger.info(
                f"Execution completed: {successful_placements} placements, "
                f"total words: {len(state.placed_words)}, status: {status}"
            )
            return updates

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            # Return error state but allow workflow to continue
            return {
                "status": "executing",
                "iteration": new_iteration,
                "metadata": {
                    **state.metadata,
                    f"execution_iteration_{new_iteration}": f"error: {str(e)}",
                }
            }

    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Determine if workflow should continue or end.

        The workflow continues if:
        1. Requirements are not yet met (min words not placed)
        2. Maximum iterations not reached
        3. No fatal errors occurred

        Args:
            state: Current agent state

        Returns:
            "continue" to continue workflow, "end" to terminate
        """
        # Handle dict input from LangGraph
        if isinstance(state, dict):
            try:
                state = AgentState(**state)
            except Exception as e:
                logger.error(f"Failed to convert dict to AgentState: {e}")
                raise

        # Check for failure status
        if state.status == "failed":
            logger.warning(f"Workflow failed: {state.error_message}")
            return "end"

        # Check for completed status (set by planner when it decides to stop)
        if state.status == "completed":
            logger.info("Workflow completed by planner decision")
            return "end"

        # Check if requirements are met
        if state.is_requirements_met():
            logger.info(
                f"Requirements met: {state.get_word_count()} words placed "
                f"(min: {state.requirements.min_words})"
            )
            return "end"

        # Check if max iterations reached
        if state.is_max_iterations_reached():
            logger.warning(
                f"Max iterations ({state.max_iterations}) reached. "
                f"Only {state.get_word_count()} words placed "
                f"(min: {state.requirements.min_words})"
            )
            # Status should already be set to "failed" by executor node
            return "end"

        # Check if we should stop based on agent decision
        if self.planner_agent.should_stop(state):
            logger.info("Planner agent decided to stop workflow")
            # Status should be set appropriately by the nodes
            return "end"

        # Continue workflow
        logger.info(
            f"Continuing workflow: iteration {state.iteration}/{state.max_iterations}, "
            f"words placed: {state.get_word_count()}/{state.requirements.min_words}"
        )
        return "continue"

    def generate_puzzle(
        self,
        topic: str,
        grid_size: int = 8,
        min_words: int = 8,
        max_words: int = 15,
        difficulty: Literal["easy", "medium", "hard"] = "medium",
        max_iterations: int = 50,
    ) -> AgentState:
        """
        Generate a crossword puzzle using the workflow.

        Args:
            topic: Topic for puzzle generation
            grid_size: Size of the grid (NxN)
            min_words: Minimum number of words to place
            max_words: Maximum number of words to place
            difficulty: Difficulty level
            max_iterations: Maximum iterations allowed

        Returns:
            Final AgentState after workflow completion

        Raises:
            ValueError: If parameters are invalid
        """
        logger.info(f"Starting puzzle generation for topic: {topic}")

        # Create requirements
        requirements = PuzzleRequirements(
            topic=topic,
            grid_size=grid_size,
            min_words=min_words,
            max_words=max_words,
            difficulty=difficulty,
        )

        # Create initial state
        initial_state = AgentState(
            requirements=requirements,
            max_iterations=max_iterations,
        )

        # Run the workflow with dynamic recursion limit
        # Calculate based on max_iterations to prevent hitting the limit
        # Each iteration involves ~4 graph node executions (initialize, planner, executor, should_continue)
        # Add 20% buffer for safety
        recursion_limit = max(100, int(max_iterations * 4 * 1.2))
        
        logger.info(
            f"Invoking workflow with max_iterations={max_iterations}, "
            f"calculated recursion_limit={recursion_limit}"
        )
        
        try:
            result = self.graph.invoke(
                initial_state,
                config={"recursion_limit": recursion_limit}
            )

            # Convert result to AgentState if it's a dict
            if isinstance(result, dict):
                final_state = AgentState(**result)
            else:
                final_state = result

            # Mark as completed if requirements met
            if final_state.is_requirements_met():
                final_state.mark_completed()

            logger.info(
                f"Puzzle generation completed: status={final_state.status}, "
                f"words={final_state.get_word_count()}, "
                f"fill_rate={final_state.get_fill_rate():.2%}"
            )

            return final_state

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            initial_state.mark_failed(str(e))
            return initial_state

    async def generate_puzzle_async(
        self,
        topic: str,
        grid_size: int = 8,
        min_words: int = 8,
        max_words: int = 15,
        difficulty: Literal["easy", "medium", "hard"] = "medium",
        max_iterations: int = 50,
    ) -> AgentState:
        """
        Generate a crossword puzzle asynchronously using the workflow.

        Args:
            topic: Topic for puzzle generation
            grid_size: Size of the grid (NxN)
            min_words: Minimum number of words to place
            max_words: Maximum number of words to place
            difficulty: Difficulty level
            max_iterations: Maximum iterations allowed

        Returns:
            Final AgentState after workflow completion

        Raises:
            ValueError: If parameters are invalid
        """
        logger.info(f"Starting async puzzle generation for topic: {topic}")

        # Create requirements
        requirements = PuzzleRequirements(
            topic=topic,
            grid_size=grid_size,
            min_words=min_words,
            max_words=max_words,
            difficulty=difficulty,
        )

        # Create initial state
        initial_state = AgentState(
            requirements=requirements,
            max_iterations=max_iterations,
        )

        # Run the workflow asynchronously
        try:
            result = await self.graph.ainvoke(initial_state)

            # Convert result to AgentState if it's a dict
            if isinstance(result, dict):
                final_state = AgentState(**result)
            else:
                final_state = result

            # Mark as completed if requirements met
            if final_state.is_requirements_met():
                final_state.mark_completed()

            logger.info(
                f"Async puzzle generation completed: status={final_state.status}, "
                f"words={final_state.get_word_count()}, "
                f"fill_rate={final_state.get_fill_rate():.2%}"
            )

            return final_state

        except Exception as e:
            logger.error(f"Async workflow execution failed: {e}", exc_info=True)
            initial_state.mark_failed(str(e))
            return initial_state


# Singleton instance for convenience
_workflow_instance: Optional[CrosswordWorkflow] = None


def get_workflow() -> CrosswordWorkflow:
    """
    Get the singleton workflow instance.

    Returns:
        CrosswordWorkflow instance
    """
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = CrosswordWorkflow()
    return _workflow_instance
