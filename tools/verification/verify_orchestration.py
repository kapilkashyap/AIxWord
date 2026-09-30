"""
Verification script for multi-agent orchestration.

This script verifies that the LangGraph workflow correctly orchestrates
the PlannerAgent and WordGeneratorAgent to generate crossword puzzles.
"""

import logging
import os
import sys

# Set dummy API key for testing
os.environ['OPENAI_API_KEY'] = 'sk-test-dummy-key-for-verification'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_workflow_initialization() -> bool:
    """Verify workflow initializes with agents."""
    try:
        from unittest.mock import MagicMock

        from backend.agents.planner import PlannerAgent
        from backend.agents.word_generator import WordGeneratorAgent
        from backend.agents.workflow import CrosswordWorkflow

        # Create agents with mocked LLM clients
        mock_llm = MagicMock()
        planner = PlannerAgent(llm_client=mock_llm)
        generator = WordGeneratorAgent(llm_client=mock_llm)

        workflow = CrosswordWorkflow(
            planner_agent=planner,
            word_generator_agent=generator
        )

        assert workflow.planner_agent is not None, "Planner agent not initialized"
        assert workflow.word_generator_agent is not None, "Word generator agent not initialized"
        assert workflow.graph is not None, "Workflow graph not initialized"

        logger.info("✓ Workflow initialization verified")
        return True
    except Exception as e:
        logger.error(f"✗ Workflow initialization failed: {e}")
        return False


def verify_workflow_singleton() -> bool:
    """Verify workflow singleton pattern."""
    try:
        from backend.agents.workflow import get_workflow

        workflow1 = get_workflow()
        workflow2 = get_workflow()

        assert workflow1 is workflow2, "Singleton pattern not working"

        logger.info("✓ Workflow singleton verified")
        return True
    except Exception as e:
        logger.error(f"✗ Workflow singleton failed: {e}")
        return False


def verify_initialize_node() -> bool:
    """Verify initialize node creates grid."""
    try:
        from backend.agents.state import AgentState, PuzzleRequirements
        from backend.agents.workflow import CrosswordWorkflow

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        updates = workflow._initialize_node(state)

        assert "grid_state" in updates, "Grid state not created"
        assert updates["status"] == "planning", "Status not set to planning"
        assert updates["iteration"] == 0, "Iteration not initialized"
        assert "metadata" in updates, "Metadata not created"

        logger.info("✓ Initialize node verified")
        return True
    except Exception as e:
        logger.error(f"✗ Initialize node failed: {e}")
        return False


def verify_planner_node_integration() -> bool:
    """Verify planner node integrates with PlannerAgent."""
    try:
        from unittest.mock import patch

        from backend.agents.planner import PlannerAction
        from backend.agents.state import AgentState, PuzzleRequirements
        from backend.agents.workflow import CrosswordWorkflow
        from backend.domain import CrosswordGrid

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Mock planner response
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
                    "reasoning": "First word"
                }
            ]
        )

        with patch.object(
            workflow.planner_agent,
            'generate_placement_plan',
            return_value=mock_action
        ):
            updates = workflow._planner_node(state)

            assert updates["status"] == "planning", "Status not set correctly"
            assert "placement_plan" in updates, "Placement plan not in updates"
            assert len(updates["placement_plan"]) == 1, "Placement plan not populated"

        logger.info("✓ Planner node integration verified")
        return True
    except Exception as e:
        logger.error(f"✗ Planner node integration failed: {e}")
        return False


def verify_executor_node_integration() -> bool:
    """Verify executor node integrates with WordGeneratorAgent."""
    try:
        from unittest.mock import patch

        from backend.agents.state import AgentState, PlacementPlan, PuzzleRequirements
        from backend.agents.workflow import CrosswordWorkflow
        from backend.domain import CrosswordGrid

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req, iteration=0)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Add placement plan
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

        # Mock executor response
        with patch.object(
            workflow.word_generator_agent,
            'execute_placement_plan',
            return_value=1
        ):
            updates = workflow._executor_node(state)

            assert updates["status"] == "executing", "Status not set correctly"
            assert updates["iteration"] == 1, "Iteration not incremented"
            assert "grid_state" in updates, "Grid state not in updates"

        logger.info("✓ Executor node integration verified")
        return True
    except Exception as e:
        logger.error(f"✗ Executor node integration failed: {e}")
        return False


def verify_should_continue_logic() -> bool:
    """Verify should_continue decision logic."""
    try:
        from backend.agents.state import AgentState, PuzzleRequirements
        from backend.agents.workflow import CrosswordWorkflow
        from backend.domain import CrosswordGrid, Direction, WordPlacement

        workflow = CrosswordWorkflow()

        # Test 1: Requirements met
        req = PuzzleRequirements(topic="Science", min_words=4)
        state = AgentState(requirements=req)
        grid = CrosswordGrid(size=8)

        # Place enough words
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
            word="HISTORY",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="Past",
            number=1,
        )
        grid.place_word(placement2)

        state.set_grid(grid)

        result = workflow._should_continue(state)
        assert result == "end", "Should end when requirements met"

        # Test 2: Max iterations reached
        req2 = PuzzleRequirements(topic="Science", min_words=10)
        state2 = AgentState(requirements=req2, max_iterations=5, iteration=5)

        result2 = workflow._should_continue(state2)
        assert result2 == "end", "Should end when max iterations reached"

        # Test 3: Normal continuation
        req3 = PuzzleRequirements(topic="Science", min_words=10)
        state3 = AgentState(requirements=req3, max_iterations=50, iteration=2)

        result3 = workflow._should_continue(state3)
        assert result3 == "continue", "Should continue in normal operation"

        logger.info("✓ Should continue logic verified")
        return True
    except Exception as e:
        logger.error(f"✗ Should continue logic failed: {e}")
        return False


def verify_workflow_graph_structure() -> bool:
    """Verify workflow graph has correct structure."""
    try:
        from backend.agents.workflow import CrosswordWorkflow

        workflow = CrosswordWorkflow()

        # Verify graph has required methods
        assert hasattr(workflow.graph, 'invoke'), "Graph missing invoke method"
        assert hasattr(workflow.graph, 'ainvoke'), "Graph missing ainvoke method"

        logger.info("✓ Workflow graph structure verified")
        return True
    except Exception as e:
        logger.error(f"✗ Workflow graph structure failed: {e}")
        return False


def verify_error_handling() -> bool:
    """Verify workflow handles errors gracefully."""
    try:
        from unittest.mock import patch

        from backend.agents.state import AgentState, PuzzleRequirements
        from backend.agents.workflow import CrosswordWorkflow
        from backend.domain import CrosswordGrid

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Test planner error handling
        with patch.object(
            workflow.planner_agent,
            'generate_placement_plan',
            side_effect=Exception("Test error")
        ):
            updates = workflow._planner_node(state)
            assert "status" in updates, "Should return updates even on error"

        # Test executor error handling
        state.iteration = 0
        with patch.object(
            workflow.word_generator_agent,
            'execute_placement_plan',
            side_effect=Exception("Test error")
        ):
            updates = workflow._executor_node(state)
            assert updates["iteration"] == 1, "Should increment iteration even on error"

        logger.info("✓ Error handling verified")
        return True
    except Exception as e:
        logger.error(f"✗ Error handling failed: {e}")
        return False


def verify_metadata_tracking() -> bool:
    """Verify workflow tracks metadata correctly."""
    try:
        from unittest.mock import patch

        from backend.agents.planner import PlannerAction
        from backend.agents.state import AgentState, PuzzleRequirements
        from backend.agents.workflow import CrosswordWorkflow
        from backend.domain import CrosswordGrid

        workflow = CrosswordWorkflow()
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Test planner metadata
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

        with patch.object(
            workflow.planner_agent,
            'generate_placement_plan',
            return_value=mock_action
        ):
            updates = workflow._planner_node(state)
            assert "metadata" in updates, "Metadata not tracked"
            metadata_key = f"planning_iteration_{state.iteration}"
            assert metadata_key in updates["metadata"], "Planning iteration not tracked"

        logger.info("✓ Metadata tracking verified")
        return True
    except Exception as e:
        logger.error(f"✗ Metadata tracking failed: {e}")
        return False


def verify_full_workflow_execution() -> bool:
    """Verify full workflow can execute end-to-end."""
    try:
        from unittest.mock import patch

        from backend.agents.planner import PlannerAction
        from backend.agents.workflow import CrosswordWorkflow

        workflow = CrosswordWorkflow()

        # Mock planner to return STOP immediately
        mock_action = PlannerAction(
            action="STOP",
            reasoning="Test complete",
            stop_reason="Testing"
        )

        with patch.object(
            workflow.planner_agent,
            'generate_placement_plan',
            return_value=mock_action
        ):
            final_state = workflow.generate_puzzle(
                topic="Science",
                grid_size=8,
                min_words=4,
                max_iterations=5,
            )

            assert final_state is not None, "Final state is None"
            assert final_state.requirements.topic == "Science", "Topic not preserved"
            assert final_state.grid_state is not None, "Grid state not created"

        logger.info("✓ Full workflow execution verified")
        return True
    except Exception as e:
        logger.error(f"✗ Full workflow execution failed: {e}")
        return False


def main() -> int:
    """Run all verification checks."""
    logger.info("=" * 60)
    logger.info("Multi-Agent Orchestration Verification")
    logger.info("=" * 60)

    checks = [
        ("Workflow Initialization", verify_workflow_initialization),
        ("Workflow Singleton", verify_workflow_singleton),
        ("Initialize Node", verify_initialize_node),
        ("Planner Node Integration", verify_planner_node_integration),
        ("Executor Node Integration", verify_executor_node_integration),
        ("Should Continue Logic", verify_should_continue_logic),
        ("Workflow Graph Structure", verify_workflow_graph_structure),
        ("Error Handling", verify_error_handling),
        ("Metadata Tracking", verify_metadata_tracking),
        ("Full Workflow Execution", verify_full_workflow_execution),
    ]

    results = []
    for name, check_func in checks:
        logger.info(f"\nVerifying: {name}")
        result = check_func()
        results.append((name, result))

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Verification Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")

    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} checks passed")
    logger.info("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
