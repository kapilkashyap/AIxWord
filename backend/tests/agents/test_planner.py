"""
Unit tests for PlannerAgent.

This module tests the PlannerAgent's ability to analyze grid state,
generate placement plans, and make strategic decisions about word placement.
"""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from backend.agents.planner import PlannerAction, PlannerAgent
from backend.agents.state import AgentState, PuzzleRequirements
from backend.domain import CrosswordGrid, Direction


class TestPlannerAgent:
    """Test suite for PlannerAgent."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return MagicMock()

    @pytest.fixture
    def planner_agent(self, mock_llm_client):
        """Create a PlannerAgent with mock LLM client."""
        return PlannerAgent(llm_client=mock_llm_client)

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
        from backend.domain.models import WordPlacement

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

    def test_initialization(self, planner_agent):
        """Test PlannerAgent initialization."""
        assert planner_agent is not None
        assert planner_agent.llm_client is not None
        assert planner_agent.prompts is not None

    def test_analyze_grid_state_empty(self, planner_agent, empty_state):
        """Test grid state analysis with empty grid."""
        analysis = planner_agent.analyze_grid_state(empty_state)

        assert analysis["grid_size"] == 8
        assert analysis["placed_words"] == []
        assert analysis["fill_rate"] == 0.0
        assert analysis["available_spaces"] == 64
        assert analysis["iteration"] == 0

    def test_analyze_grid_state_with_words(self, planner_agent, state_with_words):
        """Test grid state analysis with words placed."""
        analysis = planner_agent.analyze_grid_state(state_with_words)

        assert analysis["grid_size"] == 8
        assert "SCIENCE" in analysis["placed_words"]
        assert analysis["word_count"] == 1
        assert analysis["fill_rate"] > 0.0
        assert analysis["available_spaces"] < 64
        assert "intersections" in analysis

    def test_count_available_spaces(self, planner_agent, state_with_words):
        """Test counting available spaces on grid."""
        grid = state_with_words.get_grid()
        count = planner_agent._count_available_spaces(grid)

        # Grid is 8x8 = 64 cells, SCIENCE is 7 letters
        assert count == 64 - 7

    def test_analyze_intersections_empty(self, planner_agent, state_with_grid):
        """Test intersection analysis with no words."""
        grid = state_with_grid.get_grid()
        intersections = planner_agent._analyze_intersections(grid)

        assert intersections["count"] == 0
        assert intersections["details"] == []

    def test_analyze_intersections_with_words(self, planner_agent):
        """Test intersection analysis with intersecting words."""
        from backend.domain.models import WordPlacement

        grid = CrosswordGrid(size=8)

        # Place two intersecting words
        placement1 = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study of nature",
            number=1
        )
        placement2 = WordPlacement(
            word="CELL",
            start_row=0,
            start_col=1,
            direction=Direction.DOWN,
            clue="Basic unit of life",
            number=2
        )

        grid.place_word(placement1)
        grid.place_word(placement2)

        intersections = planner_agent._analyze_intersections(grid)

        assert intersections["count"] == 1
        assert len(intersections["details"]) == 1
        assert intersections["details"][0]["word1"] == "SCIENCE"
        assert intersections["details"][0]["word2"] == "CELL"

    def test_should_stop_planning_requirements_met(self, planner_agent, state_with_words):
        """Test stop decision when requirements are met."""
        from backend.domain.models import WordPlacement

        # Add enough words to meet requirements (min_words = 8)
        # We already have 1 word (SCIENCE), so add 7 more
        test_words = ["PHYSICS", "BIOLOGY", "GEOLOGY", "MATH", "HISTORY", "ENGLISH", "ART"]
        grid = state_with_words.get_grid()
        for i, word in enumerate(test_words):
            placement = WordPlacement(
                word=word,
                start_row=i + 1,
                start_col=0,
                direction=Direction.ACROSS,
                clue=f"Test word {i}",
                number=i + 2
            )
            grid.place_word(placement)
            state_with_words.add_placed_word(word)

        state_with_words.set_grid(grid)

        grid_analysis = planner_agent.analyze_grid_state(state_with_words)
        should_stop = planner_agent._should_stop_planning(state_with_words, grid_analysis)

        assert should_stop is True

    def test_should_stop_planning_max_iterations(self, planner_agent, state_with_words):
        """Test stop decision when max iterations reached."""
        state_with_words.iteration = 50

        grid_analysis = planner_agent.analyze_grid_state(state_with_words)
        should_stop = planner_agent._should_stop_planning(state_with_words, grid_analysis)

        assert should_stop is True

    def test_should_stop_planning_continue(self, planner_agent, state_with_words):
        """Test continue decision when requirements not met."""
        grid_analysis = planner_agent.analyze_grid_state(state_with_words)
        should_stop = planner_agent._should_stop_planning(state_with_words, grid_analysis)

        assert should_stop is False

    def test_get_stop_reason_requirements_met(self, planner_agent, state_with_words):
        """Test stop reason when requirements are met."""
        from backend.domain.models import WordPlacement

        # Add enough words to meet requirements (min_words = 8)
        # We already have 1 word (SCIENCE), so add 7 more
        test_words = ["PHYSICS", "BIOLOGY", "GEOLOGY", "MATH", "HISTORY", "ENGLISH", "ART"]
        grid = state_with_words.get_grid()
        for i, word in enumerate(test_words):
            placement = WordPlacement(
                word=word,
                start_row=i + 1,
                start_col=0,
                direction=Direction.ACROSS,
                clue=f"Test word {i}",
                number=i + 2
            )
            grid.place_word(placement)
            state_with_words.add_placed_word(word)

        state_with_words.set_grid(grid)

        grid_analysis = planner_agent.analyze_grid_state(state_with_words)
        reason = planner_agent._get_stop_reason(state_with_words, grid_analysis)

        assert "Requirements met" in reason
        assert "words placed" in reason

    def test_get_stop_reason_max_iterations(self, planner_agent, state_with_words):
        """Test stop reason when max iterations reached."""
        state_with_words.iteration = 50

        grid_analysis = planner_agent.analyze_grid_state(state_with_words)
        reason = planner_agent._get_stop_reason(state_with_words, grid_analysis)

        assert "Maximum iterations" in reason

    def test_parse_llm_response_valid(self, planner_agent):
        """Test parsing valid LLM response."""
        response = {
            "action": "ADD_WORD",
            "reasoning": "Starting with a strong anchor word",
            "word_candidates": [
                {
                    "word": "SCIENCE",
                    "clue": "Study of the natural world",
                    "priority": 0.9,
                    "category": "general"
                }
            ],
            "placement_plan": [
                {
                    "word": "SCIENCE",
                    "clue": "Study of the natural world",
                    "start_row": 0,
                    "start_col": 0,
                    "direction": "across",
                    "priority": 0.9,
                    "reasoning": "Good starting word"
                }
            ]
        }

        action = planner_agent._parse_llm_response(response)

        assert action.action == "ADD_WORD"
        assert action.reasoning == "Starting with a strong anchor word"
        assert len(action.word_candidates) == 1
        assert len(action.placement_plan) == 1

    def test_parse_llm_response_missing_action(self, planner_agent):
        """Test parsing LLM response with missing action field."""
        response = {
            "reasoning": "Some reasoning",
            "word_candidates": [
                {
                    "word": "TEST",
                    "clue": "A test",
                    "priority": 0.8
                }
            ],
            "placement_plan": []
        }

        action = planner_agent._parse_llm_response(response)

        # Should default to ADD_WORD when candidates exist
        assert action.action == "ADD_WORD"

    def test_parse_llm_response_stop_action(self, planner_agent):
        """Test parsing LLM response with STOP action."""
        response = {
            "action": "STOP",
            "reasoning": "Requirements met",
            "stop_reason": "Minimum words placed",
            "word_candidates": [],
            "placement_plan": []
        }

        action = planner_agent._parse_llm_response(response)

        assert action.action == "STOP"
        assert action.stop_reason == "Minimum words placed"

    def test_select_next_word_valid_plan(self, planner_agent, state_with_grid):
        """Test selecting next word from valid placement plan."""
        action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test",
            placement_plan=[
                {
                    "word": "SCIENCE",
                    "clue": "Study of nature",
                    "start_row": 0,
                    "start_col": 0,
                    "direction": "across",
                    "priority": 0.9,
                    "reasoning": "Good word"
                }
            ]
        )

        placement = planner_agent.select_next_word(state_with_grid, action)

        assert placement is not None
        assert placement.word == "SCIENCE"
        assert placement.start_row == 0
        assert placement.start_col == 0
        assert placement.direction == "across"

    def test_select_next_word_empty_plan(self, planner_agent, state_with_grid):
        """Test selecting next word from empty placement plan."""
        action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test",
            placement_plan=[]
        )

        placement = planner_agent.select_next_word(state_with_grid, action)

        assert placement is None

    def test_select_next_word_invalid_plan(self, planner_agent, state_with_grid):
        """Test selecting next word from invalid placement plan."""
        action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test",
            placement_plan=[
                {
                    "word": "TEST",
                    # Missing required fields
                }
            ]
        )

        placement = planner_agent.select_next_word(state_with_grid, action)

        assert placement is None

    def test_update_state_with_candidates(self, planner_agent, state_with_grid):
        """Test updating state with word candidates."""
        action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test",
            word_candidates=[
                {
                    "word": "SCIENCE",
                    "clue": "Study of nature",
                    "priority": 0.9,
                    "category": "general"
                },
                {
                    "word": "PHYSICS",
                    "clue": "Study of matter",
                    "priority": 0.8,
                    "category": "science"
                }
            ]
        )

        planner_agent.update_state_with_candidates(state_with_grid, action)

        assert len(state_with_grid.word_candidates) == 2
        assert state_with_grid.word_candidates[0].word == "SCIENCE"
        assert state_with_grid.word_candidates[1].word == "PHYSICS"

    def test_update_state_with_invalid_candidates(self, planner_agent, state_with_grid):
        """Test updating state with some invalid candidates."""
        action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test",
            word_candidates=[
                {
                    "word": "SCIENCE",
                    "clue": "Study of nature",
                    "priority": 0.9
                },
                {
                    # Missing required fields
                    "word": "INVALID"
                }
            ]
        )

        planner_agent.update_state_with_candidates(state_with_grid, action)

        # Should only add valid candidates
        assert len(state_with_grid.word_candidates) == 1
        assert state_with_grid.word_candidates[0].word == "SCIENCE"

    def test_should_stop_requirements_met(self, planner_agent, state_with_words):
        """Test should_stop when requirements are met."""
        from backend.domain.models import WordPlacement

        # Add enough words to meet requirements (min_words = 8)
        # We already have 1 word (SCIENCE), so add 7 more
        test_words = ["PHYSICS", "BIOLOGY", "GEOLOGY", "MATH", "HISTORY", "ENGLISH", "ART"]
        grid = state_with_words.get_grid()
        for i, word in enumerate(test_words):
            placement = WordPlacement(
                word=word,
                start_row=i + 1,
                start_col=0,
                direction=Direction.ACROSS,
                clue=f"Test word {i}",
                number=i + 2
            )
            grid.place_word(placement)
            state_with_words.add_placed_word(word)

        state_with_words.set_grid(grid)

        should_stop = planner_agent.should_stop(state_with_words)

        assert should_stop is True

    def test_should_stop_max_iterations(self, planner_agent, state_with_words):
        """Test should_stop when max iterations reached."""
        state_with_words.iteration = 50

        should_stop = planner_agent.should_stop(state_with_words)

        assert should_stop is True

    def test_should_stop_many_failures(self, planner_agent, state_with_words):
        """Test should_stop when too many consecutive failures."""
        for i in range(5):
            state_with_words.add_failed_placement(
                word=f"WORD{i}",
                reason="Test failure"
            )

        should_stop = planner_agent.should_stop(state_with_words)

        assert should_stop is True

    def test_should_stop_continue(self, planner_agent, state_with_words):
        """Test should_stop when should continue."""
        should_stop = planner_agent.should_stop(state_with_words)

        assert should_stop is False

    @patch('backend.agents.planner.get_llm_client')
    def test_generate_placement_plan_success(self, mock_get_client, state_with_grid):
        """Test successful placement plan generation."""
        # Setup mock LLM client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = {
            "action": "ADD_WORD",
            "reasoning": "Starting with anchor words",
            "word_candidates": [
                {
                    "word": "SCIENCE",
                    "clue": "Study of nature",
                    "priority": 0.9,
                    "category": "general"
                }
            ],
            "placement_plan": [
                {
                    "word": "SCIENCE",
                    "clue": "Study of nature",
                    "start_row": 0,
                    "start_col": 0,
                    "direction": "across",
                    "priority": 0.9,
                    "reasoning": "Good starting word"
                }
            ]
        }

        mock_client.get_json_response.return_value = mock_response

        # Create agent and generate plan
        agent = PlannerAgent()
        action = agent.generate_placement_plan(state_with_grid)

        assert action.action == "ADD_WORD"
        assert len(action.word_candidates) == 1
        assert len(action.placement_plan) == 1
        assert mock_client.get_json_response.called

    @patch('backend.agents.planner.get_llm_client')
    def test_generate_placement_plan_stop(self, mock_get_client, state_with_words):
        """Test placement plan generation when should stop."""
        from backend.domain.models import WordPlacement

        # Setup mock LLM client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Add enough words to meet requirements (min_words = 8)
        # We already have 1 word (SCIENCE), so add 7 more
        test_words = ["PHYSICS", "BIOLOGY", "GEOLOGY", "MATH", "HISTORY", "ENGLISH", "ART"]
        grid = state_with_words.get_grid()
        for i, word in enumerate(test_words):
            placement = WordPlacement(
                word=word,
                start_row=i + 1,
                start_col=0,
                direction=Direction.ACROSS,
                clue=f"Test word {i}",
                number=i + 2
            )
            grid.place_word(placement)
            state_with_words.add_placed_word(word)

        state_with_words.set_grid(grid)

        # Create agent and generate plan
        agent = PlannerAgent()
        action = agent.generate_placement_plan(state_with_words)

        # Should stop without calling LLM
        assert action.action == "STOP"
        assert action.stop_reason is not None
        assert not mock_client.get_json_response.called

    @patch('backend.agents.planner.get_llm_client')
    def test_generate_placement_plan_llm_error(self, mock_get_client, state_with_grid):
        """Test placement plan generation with LLM error."""
        # Setup mock LLM client to raise error
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_json_response.side_effect = Exception("LLM API error")

        # Create agent and attempt to generate plan
        agent = PlannerAgent()

        with pytest.raises(Exception) as exc_info:
            agent.generate_placement_plan(state_with_grid)

        assert "LLM API error" in str(exc_info.value)


class TestPlannerAction:
    """Test suite for PlannerAction model."""

    def test_planner_action_add_word(self):
        """Test creating PlannerAction for ADD_WORD."""
        action = PlannerAction(
            action="ADD_WORD",
            reasoning="Test reasoning",
            word_candidates=[
                {
                    "word": "TEST",
                    "clue": "A test",
                    "priority": 0.8
                }
            ],
            placement_plan=[]
        )

        assert action.action == "ADD_WORD"
        assert action.reasoning == "Test reasoning"
        assert len(action.word_candidates) == 1

    def test_planner_action_stop(self):
        """Test creating PlannerAction for STOP."""
        action = PlannerAction(
            action="STOP",
            reasoning="Requirements met",
            stop_reason="Minimum words placed"
        )

        assert action.action == "STOP"
        assert action.stop_reason == "Minimum words placed"

    def test_planner_action_validation_error(self):
        """Test PlannerAction validation error."""
        with pytest.raises(ValidationError):
            PlannerAction(
                # Missing required fields
                reasoning="Test"
            )
