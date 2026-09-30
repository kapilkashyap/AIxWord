"""
Tests for multi-agent orchestration in the workflow.

This module tests the integration of PlannerAgent and WordGeneratorAgent
within the LangGraph workflow.
"""

from unittest.mock import patch

import pytest

from backend.agents.planner import PlannerAction
from backend.agents.state import AgentState, PlacementPlan, PuzzleRequirements
from backend.agents.workflow import CrosswordWorkflow
from backend.domain import CrosswordGrid, Direction, WordPlacement


class TestWorkflowOrchestration:
    """Tests for workflow orchestration with real agents."""

    def test_workflow_with_agents_initialization(self) -> None:
        """Test workflow initializes with agent instances."""
        workflow = CrosswordWorkflow()

        assert workflow.planner_agent is not None
        assert workflow.word_generator_agent is not None
        assert workflow.graph is not None

    def test_workflow_with_custom_agents(self) -> None:
        """Test workflow can be initialized with custom agent instances."""
        from backend.agents.planner import PlannerAgent
        from backend.agents.word_generator import WordGeneratorAgent

        custom_planner = PlannerAgent()
        custom_generator = WordGeneratorAgent()

        workflow = CrosswordWorkflow(
            planner_agent=custom_planner,
            word_generator_agent=custom_generator,
        )

        assert workflow.planner_agent is custom_planner
        assert workflow.word_generator_agent is custom_generator

    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    def test_planner_node_with_mock(self, mock_generate_plan) -> None:
        """Test planner node with mocked agent."""
        # Setup mock response
        mock_action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test reasoning",
            word_candidates=[
                {"word": "SCIENCE", "clue": "Study of nature", "priority": 1.0}
            ],
            placement_plan=[
                {
                    "word": "SCIENCE",
                    "clue": "Study of nature",
                    "start_row": 0,
                    "start_col": 0,
                    "direction": "across",
                    "priority": 1.0,
                    "reasoning": "First word"
                }
            ]
        )
        mock_generate_plan.return_value = mock_action

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Call planner node
        updates = workflow._planner_node(state)

        # Verify planner was called
        mock_generate_plan.assert_called_once_with(state)

        # Verify updates
        assert updates["status"] == "planning"
        assert "placement_plan" in updates
        assert len(updates["placement_plan"]) == 1
        assert updates["placement_plan"][0].word == "SCIENCE"

    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    def test_planner_node_stop_action(self, mock_generate_plan) -> None:
        """Test planner node when agent decides to stop."""
        # Setup mock response with STOP action
        mock_action = PlannerAction(
            action="STOP",
            reasoning="Requirements met",
            stop_reason="Minimum words placed"
        )
        mock_generate_plan.return_value = mock_action

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Call planner node
        updates = workflow._planner_node(state)

        # Verify status is completed
        assert updates["status"] == "completed"
        assert "stop_reason" in updates["metadata"]

    @patch('backend.agents.word_generator.WordGeneratorAgent.execute_placement_plan')
    def test_executor_node_with_mock(self, mock_execute_plan) -> None:
        """Test executor node with mocked agent."""
        # Setup mock response
        mock_execute_plan.return_value = 2  # 2 successful placements

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req, iteration=0)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Add some placement plan
        state.placement_plan = [
            PlacementPlan(
                word="SCIENCE",
                clue="Study",
                start_row=0,
                start_col=0,
                direction="across",
                priority=1.0
            )
        ]

        # Call executor node
        updates = workflow._executor_node(state)

        # Verify executor was called
        mock_execute_plan.assert_called_once()

        # Verify updates
        assert updates["status"] == "executing"
        assert updates["iteration"] == 1
        assert "grid_state" in updates

    def test_executor_node_increments_iteration(self) -> None:
        """Test that executor node increments iteration counter."""
        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req, iteration=5)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Call executor node (will fail to execute but should increment)
        updates = workflow._executor_node(state)

        assert updates["iteration"] == 6

    @patch('backend.agents.planner.PlannerAgent.should_stop')
    def test_should_continue_with_agent_decision(self, mock_should_stop) -> None:
        """Test should_continue respects agent's stop decision."""
        mock_should_stop.return_value = True

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", min_words=10)
        state = AgentState(requirements=req, iteration=2)

        # Initialize grid with some words
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study",
            number=1,
        )
        grid.place_word(placement)
        state.set_grid(grid)

        # Should end because agent decided to stop
        result = workflow._should_continue(state)

        assert result == "end"
        mock_should_stop.assert_called_once_with(state)

    def test_should_continue_completed_status(self) -> None:
        """Test should_continue when status is completed."""
        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science")
        state = AgentState(requirements=req)
        state.status = "completed"

        result = workflow._should_continue(state)

        assert result == "end"

    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    @patch('backend.agents.word_generator.WordGeneratorAgent.execute_placement_plan')
    def test_full_workflow_integration(self, mock_execute, mock_plan) -> None:
        """Test full workflow with mocked agent responses."""
        # Setup mock planner response
        mock_plan.return_value = PlannerAction(
            action="ADD_WORD",
            reasoning="Planning words",
            word_candidates=[
                {"word": "SCIENCE", "clue": "Study", "priority": 1.0},
                {"word": "HISTORY", "clue": "Past", "priority": 0.9}
            ],
            placement_plan=[
                {
                    "word": "SCIENCE",
                    "clue": "Study",
                    "start_row": 0,
                    "start_col": 0,
                    "direction": "across",
                    "priority": 1.0,
                    "reasoning": "First word"
                }
            ]
        )

        # Setup mock executor response
        mock_execute.return_value = 1

        workflow = CrosswordWorkflow()

        # Run workflow with low iteration limit
        final_state = workflow.generate_puzzle(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_words=5,
            difficulty="medium",
            max_iterations=2,
        )

        # Verify workflow executed
        assert final_state is not None
        assert final_state.requirements.topic == "Science"
        assert final_state.iteration <= 2

        # Verify agents were called
        assert mock_plan.call_count >= 1
        assert mock_execute.call_count >= 1

    def test_workflow_error_handling_in_planner(self) -> None:
        """Test workflow handles errors in planner node gracefully."""
        workflow = CrosswordWorkflow()

        # Create a planner that will raise an error
        with patch.object(
            workflow.planner_agent,
            'generate_placement_plan',
            side_effect=Exception("Test error")
        ):
            req = PuzzleRequirements(topic="Science", grid_size=8)
            state = AgentState(requirements=req)

            # Initialize grid
            grid = CrosswordGrid(size=8)
            state.set_grid(grid)

            # Call planner node - should not raise, but return error state
            updates = workflow._planner_node(state)

            # Should still return updates
            assert "status" in updates
            assert "metadata" in updates

    def test_workflow_error_handling_in_executor(self) -> None:
        """Test workflow handles errors in executor node gracefully."""
        workflow = CrosswordWorkflow()

        # Create an executor that will raise an error
        with patch.object(
            workflow.word_generator_agent,
            'execute_placement_plan',
            side_effect=Exception("Test error")
        ):
            req = PuzzleRequirements(topic="Science", grid_size=8)
            state = AgentState(requirements=req, iteration=0)

            # Initialize grid
            grid = CrosswordGrid(size=8)
            state.set_grid(grid)

            # Call executor node - should not raise, but return error state
            updates = workflow._executor_node(state)

            # Should still return updates with incremented iteration
            assert updates["iteration"] == 1
            assert "metadata" in updates

    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    def test_planner_node_with_empty_plan(self, mock_generate_plan) -> None:
        """Test planner node with empty placement plan."""
        # Setup mock response with no placements
        mock_action = PlannerAction(
            action="ADD_WORD",
            reasoning="No valid placements found",
            word_candidates=[],
            placement_plan=[]
        )
        mock_generate_plan.return_value = mock_action

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Call planner node
        updates = workflow._planner_node(state)

        # Should handle empty plan gracefully
        assert updates["status"] == "planning"
        assert len(updates["placement_plan"]) == 0

    def test_workflow_state_persistence_through_nodes(self) -> None:
        """Test that state persists correctly through workflow nodes."""
        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Test", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize
        init_updates = workflow._initialize_node(state)
        state.grid_state = init_updates["grid_state"]
        state.status = init_updates["status"]
        state.iteration = init_updates["iteration"]

        # Verify grid was created
        grid = state.get_grid()
        assert grid is not None
        assert grid.size == 8

        # Place a word manually
        placement = WordPlacement(
            word="TEST",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Test word",
            number=1,
        )
        grid.place_word(placement)
        state.set_grid(grid)
        state.add_placed_word("TEST")

        # Verify state was updated
        assert state.get_word_count() == 1
        assert "TEST" in state.placed_words

        # Execute executor node
        exec_updates = workflow._executor_node(state)
        state.iteration = exec_updates["iteration"]

        # Verify iteration was incremented
        assert state.iteration == 1

    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    def test_planner_node_with_invalid_placement_plan(self, mock_generate_plan) -> None:
        """Test planner node handles invalid placement plan items."""
        # Setup mock response with invalid placement plan
        mock_action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test",
            word_candidates=[],
            placement_plan=[
                {
                    "word": "SCIENCE",
                    # Missing required fields like start_row, start_col, etc.
                }
            ]
        )
        mock_generate_plan.return_value = mock_action

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Call planner node - should handle invalid items gracefully
        updates = workflow._planner_node(state)

        # Should skip invalid items
        assert updates["status"] == "planning"
        assert len(updates["placement_plan"]) == 0  # Invalid item was skipped

    @pytest.mark.asyncio
    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    @patch('backend.agents.word_generator.WordGeneratorAgent.execute_placement_plan')
    async def test_async_workflow_integration(self, mock_execute, mock_plan) -> None:
        """Test async workflow execution."""
        # Setup mock responses
        mock_plan.return_value = PlannerAction(
            action="ADD_WORD",
            reasoning="Planning",
            word_candidates=[],
            placement_plan=[]
        )
        mock_execute.return_value = 0

        workflow = CrosswordWorkflow()

        # Run async workflow
        final_state = await workflow.generate_puzzle_async(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_iterations=2,
        )

        # Verify workflow executed
        assert final_state is not None
        assert final_state.requirements.topic == "Science"


class TestWorkflowMetadata:
    """Tests for workflow metadata tracking."""

    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    def test_planner_metadata_tracking(self, mock_generate_plan) -> None:
        """Test that planner node tracks metadata correctly."""
        mock_action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test",
            word_candidates=[
                {"word": "SCIENCE", "clue": "Study", "priority": 1.0}
            ],
            placement_plan=[
                {
                    "word": "SCIENCE",
                    "clue": "Study",
                    "start_row": 0,
                    "start_col": 0,
                    "direction": "across",
                    "priority": 1.0,
                    "reasoning": "First"
                }
            ]
        )
        mock_generate_plan.return_value = mock_action

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Call planner node
        updates = workflow._planner_node(state)

        # Verify metadata
        assert "metadata" in updates
        metadata_key = f"planning_iteration_{state.iteration}"
        assert metadata_key in updates["metadata"]
        assert updates["metadata"][metadata_key]["candidates_count"] == 1
        assert updates["metadata"][metadata_key]["placements_count"] == 1

    @patch('backend.agents.word_generator.WordGeneratorAgent.execute_placement_plan')
    def test_executor_metadata_tracking(self, mock_execute_plan) -> None:
        """Test that executor node tracks metadata correctly."""
        mock_execute_plan.return_value = 3

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req, iteration=0)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Add some placed words
        state.add_placed_word("SCIENCE")
        state.add_placed_word("HISTORY")
        state.add_placed_word("MATH")

        # Call executor node
        updates = workflow._executor_node(state)

        # Verify metadata
        assert "metadata" in updates
        metadata_key = "execution_iteration_1"
        assert metadata_key in updates["metadata"]
        assert updates["metadata"][metadata_key]["successful_placements"] == 3
        assert updates["metadata"][metadata_key]["total_words"] == 3


class TestWorkflowEdgeCases:
    """Tests for workflow edge cases and boundary conditions."""

    def test_workflow_with_zero_min_words(self) -> None:
        """Test workflow with zero minimum words (should use default)."""
        workflow = CrosswordWorkflow()

        # This should raise validation error due to Pydantic constraints
        with pytest.raises(Exception):
            workflow.generate_puzzle(
                topic="Test",
                grid_size=8,
                min_words=0,  # Invalid
            )

    def test_workflow_with_large_grid(self) -> None:
        """Test workflow with large grid size."""
        workflow = CrosswordWorkflow()

        # Should work with large grid
        final_state = workflow.generate_puzzle(
            topic="Test",
            grid_size=15,
            min_words=5,
            max_iterations=2,
        )

        assert final_state.requirements.grid_size == 15

    def test_workflow_with_single_iteration(self) -> None:
        """Test workflow with single iteration limit."""
        workflow = CrosswordWorkflow()

        final_state = workflow.generate_puzzle(
            topic="Test",
            grid_size=8,
            min_words=5,
            max_iterations=1,
        )

        # Should stop after 1 iteration
        assert final_state.iteration <= 1

    @patch('backend.agents.planner.PlannerAgent.generate_placement_plan')
    def test_workflow_with_dict_state_input(self, mock_generate_plan) -> None:
        """Test that workflow handles dict state input correctly."""
        mock_action = PlannerAction(
            action="STOP",
            reasoning="Test",
            stop_reason="Test stop"
        )
        mock_generate_plan.return_value = mock_action

        workflow = CrosswordWorkflow()

        # Create state as dict (simulating LangGraph behavior)
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        state_dict = state.to_dict()

        # Call planner node with dict
        updates = workflow._planner_node(state_dict)

        # Should handle dict input
        assert "status" in updates
