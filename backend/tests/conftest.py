"""
Pytest configuration and fixtures for backend tests.
"""

import os

import pytest

# Set dummy API key for testing
os.environ['OPENAI_API_KEY'] = 'sk-test-dummy-key-for-testing'


@pytest.fixture
def mock_llm_client():
    """Provide a mocked LLM client for testing."""
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.get_json_response.return_value = {
        "action": "STOP",
        "reasoning": "Test complete",
        "stop_reason": "Testing"
    }

    return mock_client


@pytest.fixture
def sample_puzzle_requirements():
    """Provide sample puzzle requirements for testing."""
    from backend.agents.state import PuzzleRequirements

    return PuzzleRequirements(
        topic="Science",
        grid_size=8,
        min_words=4,
        max_words=10,
        difficulty="medium"
    )


@pytest.fixture
def sample_agent_state(sample_puzzle_requirements):
    """Provide sample agent state for testing."""
    from backend.agents.state import AgentState
    from backend.domain import CrosswordGrid

    state = AgentState(requirements=sample_puzzle_requirements)
    grid = CrosswordGrid(size=8)
    state.set_grid(grid)

    return state
