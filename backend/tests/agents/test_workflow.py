"""
Tests for LangGraph workflow orchestration.

This module tests the CrosswordWorkflow and its graph structure.
"""

import pytest

from backend.agents.state import AgentState, PuzzleRequirements
from backend.agents.workflow import CrosswordWorkflow, get_workflow


class TestCrosswordWorkflow:
    """Tests for CrosswordWorkflow class."""

    def test_workflow_initialization(self) -> None:
        """Test workflow initialization."""
        workflow = CrosswordWorkflow()

        assert workflow.graph is not None

    def test_workflow_singleton(self) -> None:
        """Test workflow singleton pattern."""
        workflow1 = get_workflow()
        workflow2 = get_workflow()

        assert workflow1 is workflow2

    def test_initialize_node(self) -> None:
        """Test initialize node."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Call initialize node
        updates = workflow._initialize_node(state)

        assert "grid_state" in updates
        assert updates["status"] == "planning"
        assert updates["iteration"] == 0
        assert "metadata" in updates
        assert updates["metadata"]["topic"] == "Science"
        assert updates["metadata"]["grid_size"] == 8

    def test_planner_node_placeholder(self) -> None:
        """Test planner node (placeholder implementation)."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Science")
        state = AgentState(requirements=req)

        # Call planner node
        updates = workflow._planner_node(state)

        assert updates["status"] == "planning"
        assert "metadata" in updates

    def test_executor_node_placeholder(self) -> None:
        """Test executor node (placeholder implementation)."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Science")
        state = AgentState(requirements=req, iteration=0)

        # Call executor node
        updates = workflow._executor_node(state)

        assert updates["status"] == "executing"
        assert updates["iteration"] == 1
        assert "metadata" in updates

    def test_should_continue_requirements_met(self) -> None:
        """Test should_continue when requirements are met."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Science", min_words=4)
        state = AgentState(requirements=req)

        # Create grid with enough words
        from backend.domain import CrosswordGrid, Direction, WordPlacement

        grid = CrosswordGrid(size=8)
        placement1 = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study",
            number=1,
        )
        grid.place_word(placement1)

        placement2 = WordPlacement(
            word="MATH",
            start_row=2,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Numbers",
            number=2,
        )
        grid.place_word(placement2)

        placement3 = WordPlacement(
            word="ATOM",
            start_row=4,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Particle",
            number=3,
        )
        grid.place_word(placement3)

        placement4 = WordPlacement(
            word="CELL",
            start_row=6,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Biology unit",
            number=4,
        )
        grid.place_word(placement4)

        state.set_grid(grid)

        # Should end because requirements are met (4 words placed)
        result = workflow._should_continue(state)
        assert result == "end"

    def test_should_continue_max_iterations(self) -> None:
        """Test should_continue when max iterations reached."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Science", min_words=10)
        state = AgentState(requirements=req, max_iterations=5, iteration=5)

        # Should end because max iterations reached
        result = workflow._should_continue(state)
        assert result == "end"
        # Note: status is set by executor node, not by _should_continue
        # When testing _should_continue directly, status may not be updated

    def test_should_continue_failed_status(self) -> None:
        """Test should_continue when status is failed."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Science")
        state = AgentState(requirements=req)
        state.mark_failed("Test error")

        # Should end because status is failed
        result = workflow._should_continue(state)
        assert result == "end"

    def test_should_continue_normal(self) -> None:
        """Test should_continue in normal operation."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Science", min_words=10)
        state = AgentState(requirements=req, max_iterations=50, iteration=2)

        # Should continue
        result = workflow._should_continue(state)
        assert result == "continue"

    def test_generate_puzzle_basic(self) -> None:
        """Test basic puzzle generation (with placeholder agents)."""
        workflow = CrosswordWorkflow()

        # Generate puzzle
        final_state = workflow.generate_puzzle(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_words=5,
            difficulty="medium",
            max_iterations=3,
        )

        # Check final state
        assert final_state is not None
        assert final_state.requirements.topic == "Science"
        assert final_state.grid_state is not None

        # With placeholder implementation, it won't meet requirements
        # but should complete without errors
        assert final_state.iteration <= 3

    def test_generate_puzzle_with_parameters(self) -> None:
        """Test puzzle generation with various parameters."""
        workflow = CrosswordWorkflow()

        final_state = workflow.generate_puzzle(
            topic="History",
            grid_size=10,
            min_words=5,
            max_words=10,
            difficulty="hard",
            max_iterations=5,
        )

        assert final_state.requirements.topic == "History"
        assert final_state.requirements.grid_size == 10
        assert final_state.requirements.min_words == 5
        assert final_state.requirements.max_words == 10
        assert final_state.requirements.difficulty == "hard"

    @pytest.mark.asyncio
    async def test_generate_puzzle_async(self) -> None:
        """Test async puzzle generation."""
        workflow = CrosswordWorkflow()

        final_state = await workflow.generate_puzzle_async(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_words=5,
            difficulty="medium",
            max_iterations=3,
        )

        assert final_state is not None
        assert final_state.requirements.topic == "Science"
        assert final_state.grid_state is not None

    def test_workflow_graph_structure(self) -> None:
        """Test that workflow graph has correct structure."""
        workflow = CrosswordWorkflow()

        # Graph should be compiled
        assert workflow.graph is not None

        # Graph should have nodes
        # Note: LangGraph's compiled graph doesn't expose nodes directly,
        # but we can verify it was created without errors
        assert hasattr(workflow.graph, 'invoke')
        assert hasattr(workflow.graph, 'ainvoke')

    def test_workflow_state_updates(self) -> None:
        """Test that workflow properly updates state through nodes."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        # Initialize
        init_updates = workflow._initialize_node(state)
        assert init_updates["status"] == "planning"

        # Update state manually (simulating graph behavior)
        state.status = init_updates["status"]
        state.grid_state = init_updates["grid_state"]
        state.iteration = init_updates["iteration"]

        # Plan
        plan_updates = workflow._planner_node(state)
        assert plan_updates["status"] == "planning"

        # Execute
        exec_updates = workflow._executor_node(state)
        assert exec_updates["status"] == "executing"
        assert exec_updates["iteration"] == 1

    def test_workflow_error_handling(self) -> None:
        """Test workflow error handling."""
        workflow = CrosswordWorkflow()

        # Test with invalid grid size (should be caught by validation)
        with pytest.raises(Exception):
            workflow.generate_puzzle(
                topic="Test",
                grid_size=2,  # Too small
                min_words=5,
            )

    def test_workflow_iteration_tracking(self) -> None:
        """Test that workflow tracks iterations correctly."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req, max_iterations=5)

        # Execute multiple times
        for _i in range(3):
            updates = workflow._executor_node(state)
            state.iteration = updates["iteration"]

        assert state.iteration == 3
        assert not state.is_max_iterations_reached()

        # Execute until max
        for _i in range(2):
            updates = workflow._executor_node(state)
            state.iteration = updates["iteration"]

        assert state.iteration == 5
        assert state.is_max_iterations_reached()


class TestWorkflowIntegration:
    """Integration tests for workflow with domain models."""

    def test_workflow_with_grid_operations(self) -> None:
        """Test workflow integration with grid operations."""
        from backend.domain import Direction, WordPlacement

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize
        init_updates = workflow._initialize_node(state)
        state.grid_state = init_updates["grid_state"]

        # Get grid and place word
        grid = state.get_grid()
        assert grid is not None
        assert grid.size == 8

        placement = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study of nature",
            number=1,
        )
        grid.place_word(placement)

        # Update state
        state.set_grid(grid)
        state.add_placed_word("SCIENCE")

        # Verify state
        assert state.get_word_count() == 1
        assert "SCIENCE" in state.placed_words

    def test_workflow_state_persistence(self) -> None:
        """Test that state persists through workflow execution."""
        workflow = CrosswordWorkflow()

        final_state = workflow.generate_puzzle(
            topic="Test",
            grid_size=8,
            min_words=4,
            max_iterations=2,
        )

        # State should be preserved
        assert final_state.requirements.topic == "Test"
        assert final_state.grid_state is not None

        # Grid should be retrievable
        grid = final_state.get_grid()
        assert grid is not None
        assert grid.size == 8
