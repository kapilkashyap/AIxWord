"""
Integration smoke tests for AIxWord backend.

This module contains smoke tests that verify the integration of all major
components: domain models, agents, LLM client, and workflow orchestration.
These tests ensure that the system works end-to-end.
"""

import pytest

from backend.domain import CrosswordGrid, Direction, WordPlacement
from backend.llm.client import LLMClient
from backend.llm.prompts import PromptTemplates

# Try to import agent components - skip tests if langgraph not available
try:
    from backend.agents.state import AgentState, PuzzleRequirements, WordCandidate
    from backend.agents.workflow import CrosswordWorkflow, get_workflow
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    # Create dummy classes for type hints
    AgentState = None
    PuzzleRequirements = None
    WordCandidate = None
    CrosswordWorkflow = None
    get_workflow = None

# Skip marker for tests requiring agents
requires_agents = pytest.mark.skipif(
    not AGENTS_AVAILABLE,
    reason="langgraph not installed - agent tests skipped"
)


@pytest.mark.integration
class TestDomainIntegration:
    """Integration tests for domain components."""

    def test_grid_word_integration(self) -> None:
        """Test integration between CrosswordGrid and Word classes."""
        # Create grid
        grid = CrosswordGrid(size=8)

        # Create and place first word
        placement1 = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study of nature",
            number=1,
        )
        grid.place_word(placement1)

        # Verify word was placed
        assert len(grid.words) == 1
        word1 = grid.words[0]
        assert word1.text == "SCIENCE"
        assert word1.length == 7

        # Create and place intersecting word
        placement2 = WordPlacement(
            word="CELL",
            start_row=0,
            start_col=1,
            direction=Direction.DOWN,
            clue="Basic unit of life",
            number=2,
        )
        grid.place_word(placement2)

        # Verify both words are placed
        assert len(grid.words) == 2

        # Verify intersection
        word2 = grid.words[1]
        intersection = word1.intersects_with(word2)
        assert intersection is not None  # Words should intersect

        # Verify grid state
        assert grid.get_cell(0, 1).value == "C"  # Intersection point
        assert len(grid.words) == 2
        assert grid.get_fill_rate() > 0.0

    def test_grid_serialization_integration(self) -> None:
        """Test grid serialization and deserialization with words."""
        # Create grid with words
        grid = CrosswordGrid(size=8)

        placement1 = WordPlacement(
            word="SCIENCE",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Study of nature",
            number=1,
        )
        grid.place_word(placement1)

        placement2 = WordPlacement(
            word="CELL",
            start_row=2,
            start_col=2,
            direction=Direction.DOWN,
            clue="Basic unit",
            number=2,
        )
        grid.place_word(placement2)

        # Serialize
        grid_dict = grid.to_dict()

        # Verify serialization
        assert grid_dict["size"] == 8
        assert len(grid_dict["words"]) == 2

        # Deserialize
        restored_grid = CrosswordGrid.from_dict(grid_dict)

        # Verify restoration
        assert restored_grid.size == 8
        assert len(restored_grid.words) == 2
        assert len(restored_grid.words) == 2
        assert restored_grid.get_fill_rate() == grid.get_fill_rate()

        # Verify words are identical
        for orig_word, restored_word in zip(grid.words, restored_grid.words):
            assert orig_word.text == restored_word.text
            assert orig_word.clue == restored_word.clue
            assert orig_word.start_row == restored_word.start_row
            assert orig_word.start_col == restored_word.start_col
            assert orig_word.direction == restored_word.direction


@pytest.mark.integration
@requires_agents
class TestAgentStateIntegration:
    """Integration tests for agent state management."""

    def test_state_grid_integration(self) -> None:
        """Test AgentState integration with CrosswordGrid."""
        # Create requirements
        req = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=5,
            max_words=10,
        )

        # Create state
        state = AgentState(requirements=req)

        # Create and set grid
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="ATOM",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Smallest unit",
            number=1,
        )
        grid.place_word(placement)

        state.set_grid(grid)

        # Verify state
        assert state.get_word_count() == 1
        assert state.get_fill_rate() > 0.0

        # Retrieve grid
        retrieved_grid = state.get_grid()
        assert retrieved_grid is not None
        assert retrieved_grid.size == 8
        assert len(retrieved_grid.words) == 1

    def test_state_word_tracking(self) -> None:
        """Test state tracking of placed and failed words."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        # Add placed words
        state.add_placed_word("SCIENCE")
        state.add_placed_word("HISTORY")

        assert len(state.placed_words) == 2
        assert "SCIENCE" in state.placed_words
        assert "HISTORY" in state.placed_words

        # Add failed placement
        state.add_failed_placement(
            word="BIOLOGY",
            reason="No valid position found",
            details={"attempts": 5}
        )

        assert len(state.failed_placements) == 1
        assert state.failed_placements[0]["word"] == "BIOLOGY"
        assert state.failed_placements[0]["reason"] == "No valid position found"

    def test_state_requirements_checking(self) -> None:
        """Test state requirement validation."""
        req = PuzzleRequirements(
            topic="Science",
            min_words=4,
            max_words=10,
        )
        state = AgentState(requirements=req)

        # Initially requirements not met
        assert not state.is_requirements_met()

        # Create grid with words
        grid = CrosswordGrid(size=8)

        # Place words until requirements met
        words = ["ATOM", "CELL", "GENE", "DATA"]
        for i, word_text in enumerate(words):
            placement = WordPlacement(
                word=word_text,
                start_row=i,
                start_col=0,
                direction=Direction.ACROSS,
                clue=f"Clue {i+1}",
                number=i+1,
            )
            grid.place_word(placement)

        state.set_grid(grid)

        # Now requirements should be met
        assert state.is_requirements_met()
        assert state.get_word_count() >= req.min_words


@pytest.mark.integration
@requires_agents
class TestWorkflowIntegration:
    """Integration tests for workflow orchestration."""

    def test_workflow_initialization_flow(self) -> None:
        """Test workflow initialization creates proper state."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=5,
        )
        state = AgentState(requirements=req)

        # Run initialize node
        updates = workflow._initialize_node(state)

        # Verify updates
        assert "grid_state" in updates
        assert updates["status"] == "planning"
        assert updates["iteration"] == 0
        assert "metadata" in updates

        # Apply updates to state
        state.grid_state = updates["grid_state"]
        state.status = updates["status"]
        state.iteration = updates["iteration"]
        state.metadata = updates["metadata"]

        # Verify state is properly initialized
        grid = state.get_grid()
        assert grid is not None
        assert grid.size == 8
        assert len(grid.words) == 0

    def test_workflow_node_sequence(self) -> None:
        """Test workflow nodes execute in correct sequence."""
        workflow = CrosswordWorkflow()

        req = PuzzleRequirements(topic="Test", min_words=4)
        state = AgentState(requirements=req, max_iterations=3)

        # Initialize
        init_updates = workflow._initialize_node(state)
        state.grid_state = init_updates["grid_state"]
        state.status = init_updates["status"]
        state.iteration = init_updates["iteration"]

        # Plan
        plan_updates = workflow._planner_node(state)
        state.status = plan_updates["status"]
        assert state.status == "planning"

        # Execute
        exec_updates = workflow._executor_node(state)
        state.iteration = exec_updates["iteration"]
        state.status = exec_updates["status"]
        assert state.status == "executing"
        assert state.iteration == 1

        # Check continuation
        result = workflow._should_continue(state)
        assert result in ["continue", "end"]

    def test_workflow_singleton_pattern(self) -> None:
        """Test workflow singleton returns same instance."""
        workflow1 = get_workflow()
        workflow2 = get_workflow()

        assert workflow1 is workflow2
        assert workflow1.graph is workflow2.graph


@pytest.mark.integration
class TestLLMIntegration:
    """Integration tests for LLM components."""

    def test_llm_client_initialization(self) -> None:
        """Test LLM client initializes with config."""
        # This test verifies client can be created
        # Actual API calls are mocked in unit tests
        client = LLMClient()

        assert client.client is not None
        assert client.async_client is not None
        assert client.model is not None
        assert client.api_key is not None

    def test_prompt_templates_integration(self) -> None:
        """Test prompt templates work with state data."""
        templates = PromptTemplates()

        # Test planner prompts
        system_prompt = templates.planner_system_prompt()
        assert "crossword" in system_prompt.lower()
        assert "planner" in system_prompt.lower()

        user_prompt = templates.planner_user_prompt(
            topic="Science",
            grid_size=8,
            min_words=5,
            max_words=10,
            difficulty="medium",
            current_state={"placed_words": [], "iteration": 0},
        )

        assert "Science" in user_prompt
        assert "8" in user_prompt

        # Test word generator prompts
        word_gen_system = templates.word_generator_system_prompt()
        assert "word" in word_gen_system.lower()

        # Test clue generator prompts
        clue_system = templates.clue_generator_system_prompt()
        assert "clue" in clue_system.lower()


@pytest.mark.integration
@requires_agents
class TestEndToEndSmoke:
    """End-to-end smoke tests for the entire system."""

    def test_complete_workflow_execution(self) -> None:
        """Test complete workflow executes without errors."""
        workflow = CrosswordWorkflow()

        # Generate puzzle (with placeholder agents)
        final_state = workflow.generate_puzzle(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_words=5,
            difficulty="medium",
            max_iterations=3,
        )

        # Verify workflow completed
        assert final_state is not None
        assert final_state.status in ["completed", "failed"]
        assert final_state.iteration <= 3

        # Verify grid exists
        grid = final_state.get_grid()
        assert grid is not None
        assert grid.size == 8

    def test_state_serialization_roundtrip(self) -> None:
        """Test state can be serialized and deserialized."""
        # Create state with data
        req = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=5,
        )
        state = AgentState(requirements=req)

        # Add some data
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
        state.add_placed_word("SCIENCE")

        # Serialize
        state_dict = state.to_dict()

        # Verify serialization
        assert state_dict["requirements"]["topic"] == "Science"
        assert state_dict["grid_state"] is not None
        assert len(state_dict["placed_words"]) == 1

        # Deserialize
        restored_state = AgentState.from_dict(state_dict)

        # Verify restoration
        assert restored_state.requirements.topic == "Science"
        assert restored_state.get_word_count() == 1
        assert "SCIENCE" in restored_state.placed_words

    def test_grid_operations_with_validation(self) -> None:
        """Test grid operations with validation layer."""
        from backend.domain.validator import WordValidator

        grid = CrosswordGrid(size=8)

        # Test valid placement
        placement = WordPlacement(
            word="PYTHON",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Language",
            number=1,
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid

        # Place the word
        grid.place_word(placement)

        # Test invalid placement (overlapping)
        invalid_placement = WordPlacement(
            word="JAVA",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Another language",
            number=2,
        )

        result = WordValidator.validate_placement(grid, invalid_placement)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("conflict" in error.lower() for error in result.errors)

    def test_word_candidate_to_placement_flow(self) -> None:
        """Test flow from word candidate to placement."""
        # Create word candidate
        candidate = WordCandidate(
            word="SCIENCE",
            clue="Study of nature",
            priority=1.0,
            category="Education",
        )

        # Create placement from candidate
        placement = WordPlacement(
            word=candidate.word,
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue=candidate.clue,
            number=1,
        )

        # Place on grid
        grid = CrosswordGrid(size=8)
        grid.place_word(placement)

        # Verify placement
        assert len(grid.words) == 1
        word = grid.words[0]
        assert word.text == candidate.word
        assert word.clue == candidate.clue

    def test_multiple_word_placement_flow(self) -> None:
        """Test placing multiple words with intersections."""
        grid = CrosswordGrid(size=10)

        # Place first word
        placement1 = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study",
            number=1,
        )
        grid.place_word(placement1)

        # Place intersecting word
        placement2 = WordPlacement(
            word="CELL",
            start_row=0,
            start_col=1,
            direction=Direction.DOWN,
            clue="Unit",
            number=2,
        )
        grid.place_word(placement2)

        # Place another word (ALSO has 'L' at position 1, matching CELL's 'L' at row 2)
        placement3 = WordPlacement(
            word="ALSO",
            start_row=2,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Additionally",
            number=3,
        )
        result3 = grid.place_word(placement3)
        assert result3, "Failed to place third word"

        # Verify all words placed
        assert grid.get_word_count() == 3
        assert grid.get_fill_rate() > 0.0

        # Verify grid integrity
        for word in grid.words:
            assert word.is_complete(grid)
            assert len(word.get_cells()) == len(word.text)


@pytest.mark.integration
@pytest.mark.slow
@requires_agents
class TestComplexIntegration:
    """Complex integration tests that may take longer."""

    def test_large_grid_operations(self) -> None:
        """Test operations on larger grids."""
        grid = CrosswordGrid(size=15)

        # Place multiple words
        words = [
            ("SCIENCE", 0, 0, Direction.ACROSS),
            ("HISTORY", 2, 0, Direction.ACROSS),
            ("BIOLOGY", 4, 0, Direction.ACROSS),
            ("PHYSICS", 6, 0, Direction.ACROSS),
            ("CHEMISTRY", 8, 0, Direction.ACROSS),
        ]

        for i, (word, row, col, direction) in enumerate(words):
            placement = WordPlacement(
                word=word,
                start_row=row,
                start_col=col,
                direction=direction,
                clue=f"Clue {i+1}",
                number=i+1,
            )
            grid.place_word(placement)

        # Verify all words placed
        assert grid.get_word_count() == 5
        assert grid.get_fill_rate() > 0.0

        # Test serialization of large grid
        grid_dict = grid.to_dict()
        restored_grid = CrosswordGrid.from_dict(grid_dict)

        assert restored_grid.size == 15
        assert restored_grid.get_word_count() == 5

    def test_workflow_with_multiple_iterations(self) -> None:
        """Test workflow with multiple iterations."""
        workflow = CrosswordWorkflow()

        final_state = workflow.generate_puzzle(
            topic="Science",
            grid_size=8,
            min_words=5,
            max_words=10,
            max_iterations=10,
        )

        # Verify workflow ran
        assert final_state is not None
        assert final_state.iteration > 0
        assert final_state.iteration <= 10

        # Verify state tracking
        assert final_state.metadata is not None
        assert "initialized_at" in final_state.metadata

    def test_state_with_complex_data(self) -> None:
        """Test state handling with complex data structures."""
        req = PuzzleRequirements(
            topic="Science",
            grid_size=10,
            min_words=8,
            max_words=15,
            difficulty="hard",
        )

        state = AgentState(requirements=req, max_iterations=20)

        # Add word candidates
        candidates = [
            WordCandidate(word="ATOM", clue="Particle", priority=1.0),
            WordCandidate(word="CELL", clue="Unit", priority=0.9),
            WordCandidate(word="GENE", clue="DNA", priority=0.8),
        ]
        state.word_candidates = candidates

        # Create grid with words
        grid = CrosswordGrid(size=10)
        for i, candidate in enumerate(candidates):
            placement = WordPlacement(
                word=candidate.word,
                start_row=i * 2,
                start_col=0,
                direction=Direction.ACROSS,
                clue=candidate.clue,
                number=i+1,
            )
            grid.place_word(placement)
            state.add_placed_word(candidate.word)

        state.set_grid(grid)

        # Add failed placements
        state.add_failed_placement("MOLECULE", "Too long", {"length": 8})
        state.add_failed_placement("DNA", "No space", {"attempts": 3})

        # Verify state
        assert len(state.word_candidates) == 3
        assert len(state.placed_words) == 3
        assert len(state.failed_placements) == 2
        assert state.get_word_count() == 3

        # Test serialization
        state_dict = state.to_dict()
        restored_state = AgentState.from_dict(state_dict)

        assert len(restored_state.word_candidates) == 3
        assert len(restored_state.placed_words) == 3
        assert len(restored_state.failed_placements) == 2
