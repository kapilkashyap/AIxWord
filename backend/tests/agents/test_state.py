"""
Tests for agent state management.

This module tests the AgentState and related models used in the LangGraph workflow.
"""

import pytest

from backend.agents.state import (
    AgentState,
    PlacementPlan,
    PuzzleRequirements,
    WordCandidate,
)
from backend.domain import CrosswordGrid, Direction, WordPlacement


class TestPuzzleRequirements:
    """Tests for PuzzleRequirements model."""

    def test_create_requirements(self) -> None:
        """Test creating puzzle requirements."""
        req = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=10,
            max_words=15,
            difficulty="medium",
        )

        assert req.topic == "Science"
        assert req.grid_size == 8
        assert req.min_words == 10
        assert req.max_words == 15
        assert req.difficulty == "medium"

    def test_default_values(self) -> None:
        """Test default values for requirements."""
        req = PuzzleRequirements(topic="History")

        assert req.grid_size == 8
        assert req.min_words == 8
        assert req.max_words == 15
        assert req.difficulty == "medium"

    def test_grid_size_validation(self) -> None:
        """Test grid size validation."""
        # Valid sizes
        PuzzleRequirements(topic="Test", grid_size=4)
        PuzzleRequirements(topic="Test", grid_size=20)

        # Invalid sizes
        with pytest.raises(Exception):
            PuzzleRequirements(topic="Test", grid_size=3)

        with pytest.raises(Exception):
            PuzzleRequirements(topic="Test", grid_size=21)

    def test_difficulty_validation(self) -> None:
        """Test difficulty level validation."""
        # Valid difficulties
        PuzzleRequirements(topic="Test", difficulty="easy")
        PuzzleRequirements(topic="Test", difficulty="medium")
        PuzzleRequirements(topic="Test", difficulty="hard")

        # Invalid difficulty
        with pytest.raises(Exception):
            PuzzleRequirements(topic="Test", difficulty="extreme")  # type: ignore


class TestWordCandidate:
    """Tests for WordCandidate model."""

    def test_create_candidate(self) -> None:
        """Test creating word candidate."""
        candidate = WordCandidate(
            word="SCIENCE",
            clue="Study of the natural world",
            priority=0.9,
            category="education",
        )

        assert candidate.word == "SCIENCE"
        assert candidate.clue == "Study of the natural world"
        assert candidate.priority == 0.9
        assert candidate.category == "education"

    def test_default_priority(self) -> None:
        """Test default priority value."""
        candidate = WordCandidate(word="TEST", clue="A test")
        assert candidate.priority == 1.0
        assert candidate.category is None


class TestPlacementPlan:
    """Tests for PlacementPlan model."""

    def test_create_plan(self) -> None:
        """Test creating placement plan."""
        plan = PlacementPlan(
            word="SCIENCE",
            clue="Study of the natural world",
            start_row=0,
            start_col=0,
            direction="across",
            priority=0.9,
            reasoning="Good starting word",
        )

        assert plan.word == "SCIENCE"
        assert plan.clue == "Study of the natural world"
        assert plan.start_row == 0
        assert plan.start_col == 0
        assert plan.direction == "across"
        assert plan.priority == 0.9
        assert plan.reasoning == "Good starting word"

    def test_direction_validation(self) -> None:
        """Test direction validation."""
        # Valid directions
        PlacementPlan(
            word="TEST",
            clue="Test",
            start_row=0,
            start_col=0,
            direction="across",
        )

        PlacementPlan(
            word="TEST",
            clue="Test",
            start_row=0,
            start_col=0,
            direction="down",
        )

        # Invalid direction
        with pytest.raises(Exception):
            PlacementPlan(
                word="TEST",
                clue="Test",
                start_row=0,
                start_col=0,
                direction="diagonal",  # type: ignore
            )


class TestAgentState:
    """Tests for AgentState model."""

    def test_create_state(self) -> None:
        """Test creating agent state."""
        req = PuzzleRequirements(topic="Science")
        state = AgentState(requirements=req)

        assert state.requirements.topic == "Science"
        assert state.grid_state is None
        assert state.word_candidates == []
        assert state.placement_plan == []
        assert state.placed_words == []
        assert state.failed_placements == []
        assert state.iteration == 0
        assert state.max_iterations == 50
        assert state.status == "initializing"
        assert state.error_message is None
        assert state.metadata == {}

    def test_grid_serialization(self) -> None:
        """Test grid serialization and deserialization."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        # Create and set grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        assert state.grid_state is not None
        assert isinstance(state.grid_state, dict)

        # Retrieve grid
        retrieved_grid = state.get_grid()
        assert retrieved_grid is not None
        assert retrieved_grid.size == 8
        assert len(retrieved_grid.words) == 0

    def test_grid_with_words(self) -> None:
        """Test grid serialization with placed words."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        # Create grid and place word
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study of nature",
            number=1,
        )
        grid.place_word(placement)

        # Serialize
        state.set_grid(grid)

        # Deserialize
        retrieved_grid = state.get_grid()
        assert retrieved_grid is not None
        assert len(retrieved_grid.words) == 1
        assert retrieved_grid.words[0].text == "SCIENCE"

    def test_add_placed_word(self) -> None:
        """Test adding placed words."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        state.add_placed_word("SCIENCE")
        state.add_placed_word("HISTORY")

        assert len(state.placed_words) == 2
        assert "SCIENCE" in state.placed_words
        assert "HISTORY" in state.placed_words

    def test_add_placed_word_no_duplicates(self) -> None:
        """Test that duplicate words are not added."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        state.add_placed_word("SCIENCE")
        state.add_placed_word("SCIENCE")

        assert len(state.placed_words) == 1

    def test_add_failed_placement(self) -> None:
        """Test recording failed placements."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        state.add_failed_placement(
            word="INVALID",
            reason="Out of bounds",
            details={"row": 10, "col": 10},
        )

        assert len(state.failed_placements) == 1
        failure = state.failed_placements[0]
        assert failure["word"] == "INVALID"
        assert failure["reason"] == "Out of bounds"
        assert failure["iteration"] == 0
        assert failure["details"]["row"] == 10

    def test_increment_iteration(self) -> None:
        """Test iteration increment."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        assert state.iteration == 0

        state.increment_iteration()
        assert state.iteration == 1

        state.increment_iteration()
        assert state.iteration == 2

    def test_is_max_iterations_reached(self) -> None:
        """Test max iterations check."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req, max_iterations=5)

        assert not state.is_max_iterations_reached()

        state.iteration = 4
        assert not state.is_max_iterations_reached()

        state.iteration = 5
        assert state.is_max_iterations_reached()

        state.iteration = 6
        assert state.is_max_iterations_reached()

    def test_get_fill_rate_empty_grid(self) -> None:
        """Test fill rate for empty grid."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        # No grid
        assert state.get_fill_rate() == 0.0

        # Empty grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)
        assert state.get_fill_rate() == 0.0

    def test_get_fill_rate_with_words(self) -> None:
        """Test fill rate with placed words."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

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
        fill_rate = state.get_fill_rate()

        # 7 letters placed in 64 cells
        assert fill_rate > 0.0
        assert fill_rate < 1.0

    def test_get_word_count(self) -> None:
        """Test word count retrieval."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        # No grid
        assert state.get_word_count() == 0

        # Empty grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)
        assert state.get_word_count() == 0

        # Grid with words
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
            word="STUDY",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="Learn",
            number=2,
        )
        result2 = grid.place_word(placement2)
        assert result2, "Failed to place second word"

        state.set_grid(grid)
        assert state.get_word_count() == 2

    def test_is_requirements_met(self) -> None:
        """Test requirements satisfaction check."""
        req = PuzzleRequirements(topic="Test", min_words=4)
        state = AgentState(requirements=req)

        # No words
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)
        assert not state.is_requirements_met()

        # One word (not enough)
        placement1 = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study",
            number=1,
        )
        grid.place_word(placement1)
        state.set_grid(grid)
        assert not state.is_requirements_met()

        # Two words (still not enough)
        placement2 = WordPlacement(
            word="STUDY",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="Learn",
            number=2,
        )
        result2 = grid.place_word(placement2)
        assert result2, "Failed to place second word"
        state.set_grid(grid)
        assert not state.is_requirements_met()

        # Add two more words to meet requirement (4 total)
        # Place them in non-conflicting positions
        placement3 = WordPlacement(
            word="DATA",
            start_row=2,
            start_col=2,
            direction=Direction.ACROSS,
            clue="Information",
            number=3,
        )
        result3 = grid.place_word(placement3)
        assert result3, "Failed to place third word"
        
        placement4 = WordPlacement(
            word="CODE",
            start_row=4,
            start_col=2,
            direction=Direction.ACROSS,
            clue="Program",
            number=4,
        )
        result4 = grid.place_word(placement4)
        assert result4, "Failed to place fourth word"
        state.set_grid(grid)
        assert state.is_requirements_met()

    def test_mark_completed(self) -> None:
        """Test marking workflow as completed."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        state.mark_completed()
        assert state.status == "completed"

    def test_mark_failed(self) -> None:
        """Test marking workflow as failed."""
        req = PuzzleRequirements(topic="Test")
        state = AgentState(requirements=req)

        state.mark_failed("Test error message")
        assert state.status == "failed"
        assert state.error_message == "Test error message"

    def test_to_dict_and_from_dict(self) -> None:
        """Test state serialization and deserialization."""
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Add some data
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)
        state.add_placed_word("SCIENCE")
        state.increment_iteration()

        # Serialize
        state_dict = state.to_dict()
        assert isinstance(state_dict, dict)
        assert state_dict["requirements"]["topic"] == "Science"
        assert state_dict["iteration"] == 1

        # Deserialize
        restored_state = AgentState.from_dict(state_dict)
        assert restored_state.requirements.topic == "Science"
        assert restored_state.iteration == 1
        assert len(restored_state.placed_words) == 1
        assert restored_state.placed_words[0] == "SCIENCE"

    def test_state_with_candidates_and_plan(self) -> None:
        """Test state with word candidates and placement plan."""
        req = PuzzleRequirements(topic="Science")
        state = AgentState(requirements=req)

        # Add candidates
        state.word_candidates = [
            WordCandidate(word="SCIENCE", clue="Study", priority=0.9),
            WordCandidate(word="PHYSICS", clue="Natural science", priority=0.8),
        ]

        # Add placement plan
        state.placement_plan = [
            PlacementPlan(
                word="SCIENCE",
                clue="Study",
                start_row=0,
                start_col=0,
                direction="across",
                priority=0.9,
            ),
        ]

        assert len(state.word_candidates) == 2
        assert len(state.placement_plan) == 1
        assert state.word_candidates[0].word == "SCIENCE"
        assert state.placement_plan[0].word == "SCIENCE"
