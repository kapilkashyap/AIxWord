"""
Unit tests for WordGeneratorAgent.

This module tests the WordGeneratorAgent's ability to generate words that fit
patterns, validate placements, and execute placement plans.
"""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from backend.agents.state import AgentState, PlacementPlan, PuzzleRequirements
from backend.agents.word_generator import (
    WordGenerationResult,
    WordGeneratorAction,
    WordGeneratorAgent,
)
from backend.domain import CrosswordGrid, Direction, WordPlacement
from backend.domain.pattern import Pattern


class TestWordGeneratorAgent:
    """Test suite for WordGeneratorAgent."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return MagicMock()

    @pytest.fixture
    def word_generator_agent(self, mock_llm_client):
        """Create a WordGeneratorAgent with mock LLM client."""
        return WordGeneratorAgent(llm_client=mock_llm_client)

    @pytest.fixture
    def empty_state(self):
        """Create an empty agent state."""
        requirements = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=8,
            max_words=15,
            difficulty="medium",
        )
        return AgentState(requirements=requirements, max_iterations=50)

    @pytest.fixture
    def state_with_grid(self, empty_state):
        """Create a state with an initialized grid."""
        grid = CrosswordGrid(size=8)
        empty_state.set_grid(grid)
        return empty_state

    @pytest.fixture
    def state_with_words(self, state_with_grid):
        """Create a state with some words placed."""
        grid = state_with_grid.get_grid()

        # Place a word
        placement = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study of the natural world",
            number=1,
        )
        grid.place_word(placement)
        state_with_grid.add_placed_word("SCIENCE")
        state_with_grid.set_grid(grid)

        return state_with_grid

    @pytest.fixture
    def simple_placement_plan(self):
        """Create a simple placement plan."""
        return PlacementPlan(
            word="ATOM",
            clue="Smallest unit of matter",
            start_row=2,
            start_col=2,
            direction="across",
            priority=0.9,
            reasoning="Good science word",
        )

    def test_initialization(self, word_generator_agent):
        """Test WordGeneratorAgent initialization."""
        assert word_generator_agent is not None
        assert word_generator_agent.llm_client is not None
        assert word_generator_agent.prompts is not None

    def test_extract_pattern_empty_grid(
        self,
        word_generator_agent,
        state_with_grid,
        simple_placement_plan
    ):
        """Test pattern extraction from empty grid."""
        grid = state_with_grid.get_grid()
        pattern = word_generator_agent.extract_pattern(grid, simple_placement_plan)

        assert pattern is not None
        assert pattern.length == len(simple_placement_plan.word)
        assert pattern.is_empty  # All underscores
        assert pattern.pattern == "____"

    def test_extract_pattern_with_intersections(
        self,
        word_generator_agent,
        state_with_words
    ):
        """Test pattern extraction with intersecting words."""
        grid = state_with_words.get_grid()

        # Create a placement that intersects with SCIENCE
        # SCIENCE is at (0,0) across, so column 2 has 'I'
        placement_plan = PlacementPlan(
            word="IDEA",
            clue="Concept or thought",
            start_row=0,
            start_col=2,
            direction="down",
            priority=0.8,
            reasoning="Intersects with SCIENCE",
        )

        pattern = word_generator_agent.extract_pattern(grid, placement_plan)

        assert pattern is not None
        assert pattern.length == 4
        assert pattern.pattern[0] == "I"  # Intersects with SCIENCE at position 2
        assert not pattern.is_empty

    def test_get_intersecting_constraints_empty_grid(
        self,
        word_generator_agent,
        state_with_grid,
        simple_placement_plan
    ):
        """Test getting constraints from empty grid."""
        grid = state_with_grid.get_grid()
        constraints = word_generator_agent.get_intersecting_constraints(
            grid,
            simple_placement_plan
        )

        assert constraints == []

    def test_get_intersecting_constraints_with_words(
        self,
        word_generator_agent,
        state_with_words
    ):
        """Test getting constraints from grid with words."""
        grid = state_with_words.get_grid()

        # Create a placement that intersects with SCIENCE
        placement_plan = PlacementPlan(
            word="IDEA",
            clue="Concept or thought",
            start_row=0,
            start_col=2,
            direction="down",
            priority=0.8,
            reasoning="Intersects with SCIENCE",
        )

        constraints = word_generator_agent.get_intersecting_constraints(
            grid,
            placement_plan
        )

        assert len(constraints) == 1
        assert constraints[0]["position"] == 0
        assert constraints[0]["letter"] == "I"
        assert constraints[0]["intersecting_word"] == "SCIENCE"

    def test_generate_word_success(
        self,
        word_generator_agent,
        state_with_grid,
        simple_placement_plan,
        mock_llm_client
    ):
        """Test successful word generation."""
        # Mock LLM response
        mock_response = {
            "word": "ATOM",
            "clue": "Smallest unit of matter",
            "confidence": 0.9,
            "reasoning": "Perfect fit for science topic",
            "alternatives": ["CELL", "GENE"],
        }
        mock_llm_client.get_json_response.return_value = mock_response

        pattern = Pattern("____")
        result = word_generator_agent.generate_word(
            state_with_grid,
            simple_placement_plan,
            pattern
        )

        assert result.success
        assert result.word_result is not None
        assert result.word_result.word == "ATOM"
        assert result.word_result.clue == "Smallest unit of matter"
        assert result.word_result.confidence == 0.9
        assert mock_llm_client.get_json_response.called

    def test_generate_word_pattern_mismatch(
        self,
        word_generator_agent,
        state_with_grid,
        simple_placement_plan,
        mock_llm_client
    ):
        """Test word generation with pattern mismatch."""
        # Mock LLM response with wrong word
        mock_response = {
            "word": "SCIENCE",  # 7 letters, but pattern is 4
            "clue": "Study of nature",
            "confidence": 0.9,
        }
        mock_llm_client.get_json_response.return_value = mock_response

        pattern = Pattern("____")
        result = word_generator_agent.generate_word(
            state_with_grid,
            simple_placement_plan,
            pattern
        )

        # Should fail because word doesn't match pattern
        assert not result.success
        assert result.error_message is not None

    def test_generate_word_llm_error(
        self,
        word_generator_agent,
        state_with_grid,
        simple_placement_plan,
        mock_llm_client
    ):
        """Test word generation with LLM error."""
        # Mock LLM to raise exception
        mock_llm_client.get_json_response.side_effect = Exception("API error")

        pattern = Pattern("____")
        result = word_generator_agent.generate_word(
            state_with_grid,
            simple_placement_plan,
            pattern
        )

        assert not result.success
        assert result.error_message is not None
        assert "LLM error" in result.error_message

    def test_parse_llm_response_valid(self, word_generator_agent):
        """Test parsing valid LLM response."""
        response = {
            "word": "ATOM",
            "clue": "Smallest unit of matter",
            "confidence": 0.9,
            "reasoning": "Good fit",
            "alternatives": ["CELL"],
        }
        pattern = Pattern("____")

        result = word_generator_agent._parse_llm_response(response, pattern)

        assert result is not None
        assert result.word == "ATOM"
        assert result.clue == "Smallest unit of matter"
        assert result.confidence == 0.9

    def test_parse_llm_response_missing_fields(self, word_generator_agent):
        """Test parsing LLM response with missing fields."""
        response = {
            "word": "ATOM",
            # Missing clue
        }
        pattern = Pattern("____")

        result = word_generator_agent._parse_llm_response(response, pattern)

        assert result is None

    def test_parse_llm_response_pattern_mismatch(self, word_generator_agent):
        """Test parsing LLM response with pattern mismatch."""
        response = {
            "word": "TOOLONG",
            "clue": "This word is too long",
        }
        pattern = Pattern("____")

        result = word_generator_agent._parse_llm_response(response, pattern)

        assert result is None

    def test_execute_placement_success(
        self,
        word_generator_agent,
        state_with_grid,
        simple_placement_plan,
        mock_llm_client
    ):
        """Test successful placement execution."""
        # Mock LLM response
        mock_response = {
            "word": "ATOM",
            "clue": "Smallest unit of matter",
            "confidence": 0.9,
        }
        mock_llm_client.get_json_response.return_value = mock_response

        success = word_generator_agent.execute_placement(
            state_with_grid,
            simple_placement_plan
        )

        assert success
        assert "ATOM" in state_with_grid.placed_words

        grid = state_with_grid.get_grid()
        assert grid.get_word_count() == 1

    def test_execute_placement_already_complete(
        self,
        word_generator_agent,
        state_with_grid
    ):
        """Test placement execution when pattern is already complete."""
        grid = state_with_grid.get_grid()

        # Place a word first
        placement = WordPlacement(
            word="ATOM",
            start_row=2,
            start_col=2,
            direction=Direction.ACROSS,
            clue="Smallest unit",
            number=1,
        )
        grid.place_word(placement)
        state_with_grid.set_grid(grid)

        # Try to place the same word again
        placement_plan = PlacementPlan(
            word="ATOM",
            clue="Smallest unit",
            start_row=2,
            start_col=2,
            direction="across",
            priority=0.9,
        )

        success = word_generator_agent.execute_placement(
            state_with_grid,
            placement_plan
        )

        # Should succeed because word is already there
        assert success

    def test_execute_placement_validation_failure(
        self,
        word_generator_agent,
        state_with_grid,
        mock_llm_client
    ):
        """Test placement execution with validation failure."""
        # Mock LLM to return a word that will fail validation
        mock_response = {
            "word": "ATOM",
            "clue": "Test",
        }
        mock_llm_client.get_json_response.return_value = mock_response

        # Create a placement that goes out of bounds
        placement_plan = PlacementPlan(
            word="VERYLONGWORD",
            clue="Too long",
            start_row=0,
            start_col=0,
            direction="across",
            priority=0.5,
        )

        success = word_generator_agent.execute_placement(
            state_with_grid,
            placement_plan
        )

        # Should fail due to validation
        assert not success
        assert len(state_with_grid.failed_placements) > 0

    def test_execute_placement_plan_empty(
        self,
        word_generator_agent,
        state_with_grid
    ):
        """Test executing empty placement plan."""
        state_with_grid.placement_plan = []

        count = word_generator_agent.execute_placement_plan(state_with_grid)

        assert count == 0

    def test_execute_placement_plan_multiple(
        self,
        word_generator_agent,
        state_with_grid,
        mock_llm_client
    ):
        """Test executing multiple placements."""
        # Mock LLM responses
        mock_responses = [
            {"word": "ATOM", "clue": "Smallest unit"},
            {"word": "CELL", "clue": "Basic unit of life"},
            {"word": "GENE", "clue": "Unit of heredity"},
        ]
        mock_llm_client.get_json_response.side_effect = mock_responses

        # Create placement plan
        state_with_grid.placement_plan = [
            PlacementPlan(
                word="ATOM",
                clue="Smallest unit",
                start_row=0,
                start_col=0,
                direction="across",
                priority=0.9,
            ),
            PlacementPlan(
                word="CELL",
                clue="Basic unit",
                start_row=2,
                start_col=0,
                direction="across",
                priority=0.8,
            ),
            PlacementPlan(
                word="GENE",
                clue="Heredity unit",
                start_row=4,
                start_col=0,
                direction="across",
                priority=0.7,
            ),
        ]

        count = word_generator_agent.execute_placement_plan(
            state_with_grid,
            max_placements=3
        )

        assert count == 3
        assert len(state_with_grid.placed_words) == 3

    def test_execute_placement_plan_max_limit(
        self,
        word_generator_agent,
        state_with_grid,
        mock_llm_client
    ):
        """Test max placements limit."""
        # Mock LLM responses
        mock_responses = [
            {"word": "ATOM", "clue": "Smallest unit"},
            {"word": "CELL", "clue": "Basic unit of life"},
        ]
        mock_llm_client.get_json_response.side_effect = mock_responses

        # Create placement plan with 3 items
        state_with_grid.placement_plan = [
            PlacementPlan(
                word="ATOM",
                clue="Smallest unit",
                start_row=0,
                start_col=0,
                direction="across",
                priority=0.9,
            ),
            PlacementPlan(
                word="CELL",
                clue="Basic unit",
                start_row=2,
                start_col=0,
                direction="across",
                priority=0.8,
            ),
            PlacementPlan(
                word="GENE",
                clue="Heredity unit",
                start_row=4,
                start_col=0,
                direction="across",
                priority=0.7,
            ),
        ]

        # Limit to 2 placements
        count = word_generator_agent.execute_placement_plan(
            state_with_grid,
            max_placements=2
        )

        assert count == 2
        assert len(state_with_grid.placed_words) == 2

    def test_should_continue_requirements_met(
        self,
        word_generator_agent,
        state_with_grid
    ):
        """Test should_continue when requirements are met."""
        # Add enough words to meet requirements
        grid = state_with_grid.get_grid()
        test_words = ["ATOM", "CELL", "GENE", "LIFE", "STAR", "MOON", "MARS", "NOVA"]
        for i, word in enumerate(test_words):
            placement = WordPlacement(
                word=word,
                start_row=i,
                start_col=0,
                direction=Direction.ACROSS,
                clue=f"Test word {i}",
                number=i+1,
            )
            if grid.place_word(placement):
                state_with_grid.add_placed_word(word)
        state_with_grid.set_grid(grid)

        should_continue = word_generator_agent.should_continue(state_with_grid)

        assert not should_continue

    def test_should_continue_max_iterations(
        self,
        word_generator_agent,
        state_with_grid
    ):
        """Test should_continue when max iterations reached."""
        state_with_grid.iteration = state_with_grid.max_iterations

        should_continue = word_generator_agent.should_continue(state_with_grid)

        assert not should_continue

    def test_should_continue_normal(
        self,
        word_generator_agent,
        state_with_grid
    ):
        """Test should_continue in normal conditions."""
        should_continue = word_generator_agent.should_continue(state_with_grid)

        assert should_continue


class TestWordGenerationResult:
    """Test suite for WordGenerationResult model."""

    def test_creation_minimal(self):
        """Test creating WordGenerationResult with minimal fields."""
        result = WordGenerationResult(
            word="ATOM",
            clue="Smallest unit of matter"
        )

        assert result.word == "ATOM"
        assert result.clue == "Smallest unit of matter"
        assert result.confidence == 0.8  # Default
        assert result.reasoning == ""
        assert result.alternatives == []

    def test_creation_full(self):
        """Test creating WordGenerationResult with all fields."""
        result = WordGenerationResult(
            word="ATOM",
            clue="Smallest unit of matter",
            confidence=0.95,
            reasoning="Perfect fit for science topic",
            alternatives=["CELL", "GENE", "MOLECULE"]
        )

        assert result.word == "ATOM"
        assert result.clue == "Smallest unit of matter"
        assert result.confidence == 0.95
        assert result.reasoning == "Perfect fit for science topic"
        assert len(result.alternatives) == 3

    def test_confidence_validation(self):
        """Test confidence score validation."""
        # Valid confidence
        result = WordGenerationResult(
            word="ATOM",
            clue="Test",
            confidence=0.5
        )
        assert result.confidence == 0.5

        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            WordGenerationResult(
                word="ATOM",
                clue="Test",
                confidence=1.5
            )

        # Invalid confidence (negative)
        with pytest.raises(ValidationError):
            WordGenerationResult(
                word="ATOM",
                clue="Test",
                confidence=-0.1
            )


class TestWordGeneratorAction:
    """Test suite for WordGeneratorAction model."""

    def test_success_action(self):
        """Test creating successful action."""
        word_result = WordGenerationResult(
            word="ATOM",
            clue="Smallest unit"
        )

        action = WordGeneratorAction(
            success=True,
            word_result=word_result
        )

        assert action.success
        assert action.word_result is not None
        assert action.error_message is None
        assert not action.should_retry

    def test_failure_action(self):
        """Test creating failure action."""
        action = WordGeneratorAction(
            success=False,
            error_message="Pattern mismatch",
            should_retry=True
        )

        assert not action.success
        assert action.word_result is None
        assert action.error_message == "Pattern mismatch"
        assert action.should_retry
