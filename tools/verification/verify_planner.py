#!/usr/bin/env python3
"""
Verification script for PlannerAgent implementation.

This script demonstrates the PlannerAgent's capabilities:
1. Analyzing grid state
2. Generating placement plans
3. Making strategic decisions
"""

import logging
import sys
from unittest.mock import MagicMock

# Add current directory to path for imports
sys.path.insert(0, '.')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def verify_planner_initialization():
    """Verify PlannerAgent can be initialized."""
    from agents.planner import PlannerAgent

    logger.info("Testing PlannerAgent initialization...")

    # Create mock LLM client
    mock_llm = MagicMock()
    agent = PlannerAgent(llm_client=mock_llm)

    assert agent is not None
    assert agent.llm_client is not None
    assert agent.prompts is not None

    logger.info("✓ PlannerAgent initialized successfully")
    return True


def verify_grid_analysis():
    """Verify PlannerAgent can analyze grid state."""
    from agents.planner import PlannerAgent
    from agents.state import AgentState, PuzzleRequirements
    from domain import CrosswordGrid, Direction
    from domain.models import WordPlacement

    logger.info("Testing grid state analysis...")

    # Create agent
    mock_llm = MagicMock()
    agent = PlannerAgent(llm_client=mock_llm)

    # Create state with grid
    requirements = PuzzleRequirements(
        topic="Science",
        grid_size=8,
        min_words=8,
        max_words=15,
        difficulty="medium"
    )
    state = AgentState(requirements=requirements)

    # Initialize grid
    grid = CrosswordGrid(size=8)
    placement = WordPlacement(
        word="SCIENCE",
        start_row=0,
        start_col=0,
        direction=Direction.ACROSS,
        clue="Study of the natural world",
        number=1
    )
    grid.place_word(placement)
    state.set_grid(grid)
    state.add_placed_word("SCIENCE")

    # Analyze grid
    analysis = agent.analyze_grid_state(state)

    assert analysis["grid_size"] == 8
    assert "SCIENCE" in analysis["placed_words"]
    assert analysis["word_count"] == 1
    assert analysis["fill_rate"] > 0.0

    logger.info(f"✓ Grid analysis successful: {analysis['word_count']} words, "
                f"{analysis['fill_rate']:.1%} fill rate")
    return True


def verify_stop_conditions():
    """Verify PlannerAgent stop condition logic."""
    from agents.planner import PlannerAgent
    from agents.state import AgentState, PuzzleRequirements
    from domain import CrosswordGrid, Direction
    from domain.models import WordPlacement

    logger.info("Testing stop condition logic...")

    # Create agent
    mock_llm = MagicMock()
    agent = PlannerAgent(llm_client=mock_llm)

    # Create state with enough words
    requirements = PuzzleRequirements(
        topic="Science",
        grid_size=8,
        min_words=8,
        max_words=15,
        difficulty="medium"
    )
    state = AgentState(requirements=requirements)

    # Add 8 words to meet requirements
    grid = CrosswordGrid(size=8)
    words = ["SCIENCE", "PHYSICS", "BIOLOGY", "GEOLOGY", "MATH", "HISTORY", "ENGLISH", "ART"]
    for i, word in enumerate(words):
        placement = WordPlacement(
            word=word,
            start_row=i,
            start_col=0,
            direction=Direction.ACROSS,
            clue=f"Test word {i}",
            number=i + 1
        )
        grid.place_word(placement)
        state.add_placed_word(word)

    state.set_grid(grid)

    # Check stop condition
    should_stop = agent.should_stop(state)

    assert should_stop is True
    logger.info(f"✓ Stop condition correctly detected with {state.get_word_count()} words")
    return True


def verify_llm_response_parsing():
    """Verify PlannerAgent can parse LLM responses."""
    from agents.planner import PlannerAction, PlannerAgent

    logger.info("Testing LLM response parsing...")

    # Create agent
    mock_llm = MagicMock()
    agent = PlannerAgent(llm_client=mock_llm)

    # Test valid response
    response = {
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

    action = agent._parse_llm_response(response)

    assert isinstance(action, PlannerAction)
    assert action.action == "ADD_WORD"
    assert len(action.word_candidates) == 1
    assert len(action.placement_plan) == 1

    logger.info("✓ LLM response parsing successful")
    return True


def main():
    """Run all verification tests."""
    logger.info("=" * 60)
    logger.info("PlannerAgent Verification")
    logger.info("=" * 60)

    tests = [
        ("Initialization", verify_planner_initialization),
        ("Grid Analysis", verify_grid_analysis),
        ("Stop Conditions", verify_stop_conditions),
        ("LLM Response Parsing", verify_llm_response_parsing),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            logger.info(f"\n{name}:")
            if test_func():
                passed += 1
        except Exception as e:
            logger.error(f"✗ {name} failed: {e}")
            failed += 1

    logger.info("\n" + "=" * 60)
    logger.info(f"Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
