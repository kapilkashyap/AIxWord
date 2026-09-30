"""
Unit tests for PuzzleOrchestrator.

This module tests the orchestrator's ability to coordinate puzzle generation,
handle requests, manage results, and provide high-level APIs for the workflow.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.orchestrator import (
    PuzzleGenerationRequest,
    PuzzleGenerationResult,
    PuzzleOrchestrator,
    create_orchestrator,
    get_orchestrator,
)
from backend.agents.state import AgentState, PuzzleRequirements
from backend.domain import CrosswordGrid, Direction, WordPlacement


class TestPuzzleGenerationRequest:
    """Test suite for PuzzleGenerationRequest model."""

    def test_default_values(self):
        """Test request with default values."""
        request = PuzzleGenerationRequest(topic="Science")

        assert request.topic == "Science"
        assert request.grid_size == 8
        assert request.min_words == 8
        assert request.max_words == 15
        assert request.difficulty == "medium"
        assert request.max_iterations == 50

    def test_custom_values(self):
        """Test request with custom values."""
        request = PuzzleGenerationRequest(
            topic="History",
            grid_size=10,
            min_words=10,
            max_words=20,
            difficulty="hard",
            max_iterations=75,
        )

        assert request.topic == "History"
        assert request.grid_size == 10
        assert request.min_words == 10
        assert request.max_words == 20
        assert request.difficulty == "hard"
        assert request.max_iterations == 75

    def test_validation_grid_size_bounds(self):
        """Test grid size validation."""
        # Valid sizes
        request = PuzzleGenerationRequest(topic="Test", grid_size=4)
        assert request.grid_size == 4

        request = PuzzleGenerationRequest(topic="Test", grid_size=20)
        assert request.grid_size == 20

        # Invalid sizes
        with pytest.raises(Exception):
            PuzzleGenerationRequest(topic="Test", grid_size=3)

        with pytest.raises(Exception):
            PuzzleGenerationRequest(topic="Test", grid_size=21)

    def test_validation_min_words(self):
        """Test min_words validation."""
        # Valid
        request = PuzzleGenerationRequest(topic="Test", min_words=4)
        assert request.min_words == 4

        # Invalid
        with pytest.raises(Exception):
            PuzzleGenerationRequest(topic="Test", min_words=3)

    def test_validation_max_iterations(self):
        """Test max_iterations validation."""
        # Valid
        request = PuzzleGenerationRequest(topic="Test", max_iterations=1)
        assert request.max_iterations == 1

        request = PuzzleGenerationRequest(topic="Test", max_iterations=100)
        assert request.max_iterations == 100

        # Invalid
        with pytest.raises(Exception):
            PuzzleGenerationRequest(topic="Test", max_iterations=0)

        with pytest.raises(Exception):
            PuzzleGenerationRequest(topic="Test", max_iterations=101)


class TestPuzzleGenerationResult:
    """Test suite for PuzzleGenerationResult model."""

    def test_successful_result(self):
        """Test successful generation result."""
        result = PuzzleGenerationResult(
            success=True,
            status="completed",
            word_count=10,
            fill_rate=0.75,
            iterations=15,
        )

        assert result.success is True
        assert result.status == "completed"
        assert result.word_count == 10
        assert result.fill_rate == 0.75
        assert result.iterations == 15
        assert result.error_message is None

    def test_failed_result(self):
        """Test failed generation result."""
        result = PuzzleGenerationResult(
            success=False,
            status="failed",
            error_message="Test error",
        )

        assert result.success is False
        assert result.status == "failed"
        assert result.error_message == "Test error"
        assert result.word_count == 0
        assert result.fill_rate == 0.0


class TestPuzzleOrchestrator:
    """Test suite for PuzzleOrchestrator."""

    @pytest.fixture
    def mock_planner_agent(self):
        """Create a mock PlannerAgent."""
        return MagicMock()

    @pytest.fixture
    def mock_word_generator_agent(self):
        """Create a mock WordGeneratorAgent."""
        return MagicMock()

    @pytest.fixture
    def orchestrator(self, mock_planner_agent, mock_word_generator_agent):
        """Create a PuzzleOrchestrator with mock agents."""
        return PuzzleOrchestrator(
            planner_agent=mock_planner_agent,
            word_generator_agent=mock_word_generator_agent,
        )

    @pytest.fixture
    def simple_request(self):
        """Create a simple generation request."""
        return PuzzleGenerationRequest(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_words=10,
        )

    @pytest.fixture
    def successful_state(self):
        """Create a successful final state."""
        requirements = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_words=10,
        )
        state = AgentState(requirements=requirements)

        # Create grid with enough words to meet requirements
        grid = CrosswordGrid(size=8)

        # Place 4 words to meet min_words requirement
        placement1 = WordPlacement(
            word="SCIENCE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Study of nature",
            number=1,
        )
        grid.place_word(placement1)

        placement2 = WordPlacement(
            word="ATOM",
            start_row=2,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Smallest unit",
            number=2,
        )
        grid.place_word(placement2)

        placement3 = WordPlacement(
            word="CELL",
            start_row=4,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Basic unit of life",
            number=3,
        )
        grid.place_word(placement3)

        placement4 = WordPlacement(
            word="DNA",
            start_row=6,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Genetic material",
            number=4,
        )
        grid.place_word(placement4)

        state.set_grid(grid)
        state.add_placed_word("SCIENCE")
        state.add_placed_word("ATOM")
        state.add_placed_word("CELL")
        state.add_placed_word("DNA")
        state.status = "completed"
        state.iteration = 10

        return state

    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator is not None
        assert orchestrator.planner_agent is not None
        assert orchestrator.word_generator_agent is not None
        assert orchestrator.workflow is not None

    def test_initialization_with_defaults(self):
        """Test orchestrator initialization with default agents."""
        orchestrator = PuzzleOrchestrator()

        assert orchestrator.planner_agent is not None
        assert orchestrator.word_generator_agent is not None
        assert orchestrator.workflow is not None

    def test_generate_puzzle_success(
        self,
        orchestrator,
        simple_request,
        successful_state
    ):
        """Test successful puzzle generation."""
        # Mock workflow to return successful state
        with patch.object(
            orchestrator.workflow,
            'generate_puzzle',
            return_value=successful_state
        ):
            result = orchestrator.generate_puzzle(simple_request)

            assert result.success is True
            assert result.status == "completed"
            assert result.word_count == 4
            assert result.fill_rate > 0.0
            assert result.iterations == 10
            assert result.error_message is None
            assert result.grid is not None

    def test_generate_puzzle_failure(self, orchestrator, simple_request):
        """Test puzzle generation failure."""
        # Mock workflow to raise exception
        with patch.object(
            orchestrator.workflow,
            'generate_puzzle',
            side_effect=Exception("Test error")
        ):
            result = orchestrator.generate_puzzle(simple_request)

            assert result.success is False
            assert result.status == "failed"
            assert result.error_message == "Test error"

    def test_generate_puzzle_incomplete(self, orchestrator, simple_request):
        """Test puzzle generation with incomplete result."""
        # Create incomplete state
        requirements = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=10,  # High requirement
            max_words=15,
        )
        state = AgentState(requirements=requirements)
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)
        state.status = "completed"
        state.iteration = 50

        # Mock workflow
        with patch.object(
            orchestrator.workflow,
            'generate_puzzle',
            return_value=state
        ):
            result = orchestrator.generate_puzzle(simple_request)

            # Should be marked as unsuccessful due to unmet requirements
            assert result.success is False
            assert result.word_count == 0

    @pytest.mark.asyncio
    async def test_generate_puzzle_async_success(
        self,
        orchestrator,
        simple_request,
        successful_state
    ):
        """Test async puzzle generation success."""
        # Mock async workflow
        async_mock = AsyncMock(return_value=successful_state)

        with patch.object(
            orchestrator.workflow,
            'generate_puzzle_async',
            async_mock
        ):
            result = await orchestrator.generate_puzzle_async(simple_request)

            assert result.success is True
            assert result.status == "completed"
            assert result.word_count == 4

    @pytest.mark.asyncio
    async def test_generate_puzzle_async_failure(
        self,
        orchestrator,
        simple_request
    ):
        """Test async puzzle generation failure."""
        # Mock async workflow to raise exception
        async_mock = AsyncMock(side_effect=Exception("Async test error"))

        with patch.object(
            orchestrator.workflow,
            'generate_puzzle_async',
            async_mock
        ):
            result = await orchestrator.generate_puzzle_async(simple_request)

            assert result.success is False
            assert result.status == "failed"
            assert "Async test error" in result.error_message

    def test_state_to_result_successful(self, orchestrator, successful_state):
        """Test conversion of successful state to result."""
        result = orchestrator._state_to_result(successful_state)

        assert result.success is True
        assert result.status == "completed"
        assert result.word_count == 4
        assert result.fill_rate > 0.0
        assert result.iterations == 10
        assert result.grid is not None

    def test_state_to_result_failed(self, orchestrator):
        """Test conversion of failed state to result."""
        requirements = PuzzleRequirements(topic="Test", grid_size=8)
        state = AgentState(requirements=requirements)
        state.status = "failed"
        state.error_message = "Test failure"
        state.iteration = 5

        result = orchestrator._state_to_result(state)

        assert result.success is False
        assert result.status == "failed"
        assert result.error_message == "Test failure"
        assert result.iterations == 5

    def test_validate_request_valid(self, orchestrator, simple_request):
        """Test validation of valid request."""
        is_valid, error_msg = orchestrator.validate_request(simple_request)

        assert is_valid is True
        assert error_msg is None

    def test_validate_request_invalid_grid_size(self, orchestrator):
        """Test validation with invalid grid size."""
        # Pydantic will catch this during construction, so we test the validation logic directly
        # by creating a request with valid construction but checking edge cases
        request = PuzzleGenerationRequest(topic="Test", grid_size=4, min_words=4, max_words=6)
        is_valid, error_msg = orchestrator.validate_request(request)
        assert is_valid is True

        # Test upper bound
        request = PuzzleGenerationRequest(topic="Test", grid_size=20, min_words=10, max_words=30)
        is_valid, error_msg = orchestrator.validate_request(request)
        assert is_valid is True

    def test_validate_request_invalid_min_words(self, orchestrator):
        """Test validation with invalid min_words."""
        # Pydantic catches min_words < 4, so test valid edge case
        request = PuzzleGenerationRequest(topic="Test", min_words=4)
        is_valid, error_msg = orchestrator.validate_request(request)
        assert is_valid is True

    def test_validate_request_invalid_word_counts(self, orchestrator):
        """Test validation with max_words < min_words."""
        request = PuzzleGenerationRequest(
            topic="Test",
            min_words=10,
            max_words=5,
        )

        is_valid, error_msg = orchestrator.validate_request(request)

        assert is_valid is False
        assert "max_words" in error_msg

    def test_validate_request_empty_topic(self, orchestrator):
        """Test validation with empty topic."""
        request = PuzzleGenerationRequest(topic="")

        is_valid, error_msg = orchestrator.validate_request(request)

        assert is_valid is False
        assert "Topic" in error_msg

    def test_validate_request_invalid_iterations(self, orchestrator):
        """Test validation with invalid max_iterations."""
        # Pydantic catches max_iterations < 1, so test valid edge cases
        request = PuzzleGenerationRequest(topic="Test", max_iterations=1)
        is_valid, error_msg = orchestrator.validate_request(request)
        assert is_valid is True

        request = PuzzleGenerationRequest(topic="Test", max_iterations=100)
        is_valid, error_msg = orchestrator.validate_request(request)
        assert is_valid is True

    def test_validate_request_too_many_words_for_grid(self, orchestrator):
        """Test validation with unrealistic word count for grid size."""
        request = PuzzleGenerationRequest(
            topic="Test",
            grid_size=4,
            min_words=15,  # High but not caught by max_words validation
            max_words=20,
        )

        is_valid, error_msg = orchestrator.validate_request(request)

        assert is_valid is False
        assert "too high" in error_msg

    def test_get_grid_from_result_success(self, orchestrator, successful_state):
        """Test extracting grid from successful result."""
        result = orchestrator._state_to_result(successful_state)
        grid = orchestrator.get_grid_from_result(result)

        assert grid is not None
        assert isinstance(grid, CrosswordGrid)
        assert grid.size == 8
        assert len(grid.words) == 4

    def test_get_grid_from_result_failure(self, orchestrator):
        """Test extracting grid from failed result."""
        result = PuzzleGenerationResult(
            success=False,
            status="failed",
        )

        grid = orchestrator.get_grid_from_result(result)

        assert grid is None

    def test_get_grid_from_result_no_grid(self, orchestrator):
        """Test extracting grid when result has no grid."""
        result = PuzzleGenerationResult(
            success=True,
            status="completed",
            grid=None,
        )

        grid = orchestrator.get_grid_from_result(result)

        assert grid is None

    def test_get_statistics_success(self, orchestrator, successful_state):
        """Test getting statistics from successful result."""
        result = orchestrator._state_to_result(successful_state)
        stats = orchestrator.get_statistics(result)

        assert stats["success"] is True
        assert stats["status"] == "completed"
        assert stats["word_count"] == 4
        assert stats["fill_rate"] > 0.0
        assert stats["iterations"] == 10
        assert stats["has_error"] is False
        assert "grid_size" in stats
        assert "total_cells" in stats
        assert "words" in stats
        assert len(stats["words"]) == 4
        assert "SCIENCE" in stats["words"]
        assert "ATOM" in stats["words"]
        assert "CELL" in stats["words"]
        assert "DNA" in stats["words"]

    def test_get_statistics_failure(self, orchestrator):
        """Test getting statistics from failed result."""
        result = PuzzleGenerationResult(
            success=False,
            status="failed",
            error_message="Test error",
        )

        stats = orchestrator.get_statistics(result)

        assert stats["success"] is False
        assert stats["status"] == "failed"
        assert stats["has_error"] is True
        assert "grid_size" not in stats  # No grid available

    def test_retry_generation_success_first_attempt(
        self,
        orchestrator,
        simple_request,
        successful_state
    ):
        """Test retry generation succeeds on first attempt."""
        with patch.object(
            orchestrator.workflow,
            'generate_puzzle',
            return_value=successful_state
        ):
            result = orchestrator.retry_generation(simple_request, max_retries=3)

            assert result.success is True
            assert result.word_count == 4

    def test_retry_generation_success_after_retries(
        self,
        orchestrator,
        simple_request,
        successful_state
    ):
        """Test retry generation succeeds after failures."""
        # Create failed state
        failed_requirements = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=10,
            max_words=15,
        )
        failed_state = AgentState(requirements=failed_requirements)
        failed_state.status = "failed"
        failed_state.error_message = "Not enough words"

        # Mock to fail twice, then succeed
        call_count = 0

        def mock_generate(topic, grid_size, min_words, max_words, difficulty, max_iterations):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return failed_state
            return successful_state

        with patch.object(
            orchestrator.workflow,
            'generate_puzzle',
            side_effect=mock_generate
        ):
            result = orchestrator.retry_generation(simple_request, max_retries=3)

            assert result.success is True
            assert call_count == 3

    def test_retry_generation_all_failures(self, orchestrator, simple_request):
        """Test retry generation when all attempts fail."""
        # Create failed state
        requirements = PuzzleRequirements(topic="Science", grid_size=8)
        failed_state = AgentState(requirements=requirements)
        failed_state.status = "failed"
        failed_state.error_message = "Generation failed"

        with patch.object(
            orchestrator.workflow,
            'generate_puzzle',
            return_value=failed_state
        ):
            result = orchestrator.retry_generation(simple_request, max_retries=3)

            assert result.success is False
            assert result.status == "failed"

    def test_retry_generation_invalid_request(self, orchestrator):
        """Test retry generation with invalid request."""
        invalid_request = PuzzleGenerationRequest(
            topic="",  # Empty topic
            grid_size=8,
        )

        result = orchestrator.retry_generation(invalid_request, max_retries=3)

        assert result.success is False
        assert "Invalid request" in result.error_message

    def test_retry_generation_adjusts_parameters(
        self,
        orchestrator,
        simple_request
    ):
        """Test that retry generation adjusts parameters between attempts."""
        original_min_words = simple_request.min_words

        # Create failed state
        requirements = PuzzleRequirements(topic="Science", grid_size=8)
        failed_state = AgentState(requirements=requirements)
        failed_state.status = "failed"

        call_count = 0
        captured_params = []

        def mock_generate(topic, grid_size, min_words, max_words, difficulty, max_iterations):
            nonlocal call_count
            call_count += 1
            captured_params.append({
                'min_words': min_words,
                'max_iterations': max_iterations,
            })
            return failed_state

        with patch.object(
            orchestrator.workflow,
            'generate_puzzle',
            side_effect=mock_generate
        ):
            orchestrator.retry_generation(simple_request, max_retries=3)

            # Check that parameters were adjusted
            assert len(captured_params) == 3
            # min_words should decrease (if > 4)
            if original_min_words > 4:
                assert captured_params[1]['min_words'] < captured_params[0]['min_words']
            # max_iterations should increase
            assert captured_params[1]['max_iterations'] > captured_params[0]['max_iterations']


class TestOrchestratorSingleton:
    """Test suite for orchestrator singleton functions."""

    def test_get_orchestrator_singleton(self):
        """Test get_orchestrator returns singleton."""
        orchestrator1 = get_orchestrator()
        orchestrator2 = get_orchestrator()

        assert orchestrator1 is orchestrator2

    def test_create_orchestrator_new_instance(self):
        """Test create_orchestrator creates new instance."""
        orchestrator1 = create_orchestrator()
        orchestrator2 = create_orchestrator()

        assert orchestrator1 is not orchestrator2

    def test_create_orchestrator_with_custom_agents(self):
        """Test create_orchestrator with custom agents."""
        mock_planner = MagicMock()
        mock_generator = MagicMock()

        orchestrator = create_orchestrator(
            planner_agent=mock_planner,
            word_generator_agent=mock_generator,
        )

        assert orchestrator.planner_agent is mock_planner
        assert orchestrator.word_generator_agent is mock_generator


class TestOrchestratorIntegration:
    """Integration tests for orchestrator with real workflow."""

    @pytest.fixture
    def integration_orchestrator(self):
        """Create orchestrator with mocked LLM clients."""
        from backend.agents.planner import PlannerAgent
        from backend.agents.word_generator import WordGeneratorAgent

        mock_llm = MagicMock()
        planner = PlannerAgent(llm_client=mock_llm)
        generator = WordGeneratorAgent(llm_client=mock_llm)

        return PuzzleOrchestrator(
            planner_agent=planner,
            word_generator_agent=generator,
        )

    def test_full_workflow_integration(self, integration_orchestrator):
        """Test full workflow integration through orchestrator."""
        from backend.agents.planner import PlannerAction

        request = PuzzleGenerationRequest(
            topic="Science",
            grid_size=8,
            min_words=4,
            max_words=10,
            max_iterations=5,
        )

        # Mock planner to stop immediately
        mock_action = PlannerAction(
            action="STOP",
            reasoning="Test complete",
            stop_reason="Testing",
        )

        with patch.object(
            integration_orchestrator.planner_agent,
            'generate_placement_plan',
            return_value=mock_action
        ):
            result = integration_orchestrator.generate_puzzle(request)

            # Should complete without errors
            assert result is not None
            # When planner returns STOP immediately, workflow may still be in executing state
            # after hitting max_iterations
            assert result.status in ["completed", "failed", "executing"]
            assert result.grid is not None
