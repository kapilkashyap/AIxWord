"""
Verification script for WordGeneratorAgent implementation.

This script verifies that the WordGeneratorAgent is properly implemented
and can perform its core functions without errors.
"""

import sys

from backend.agents.state import AgentState, PlacementPlan, PuzzleRequirements
from backend.agents.word_generator import WordGeneratorAgent
from backend.domain import CrosswordGrid, Direction, WordPlacement
from backend.domain.pattern import Pattern


def verify_initialization() -> bool:
    """Verify WordGeneratorAgent can be initialized."""
    print("Testing WordGeneratorAgent initialization...")
    try:
        agent = WordGeneratorAgent()
        assert agent is not None
        assert agent.llm_client is not None
        assert agent.prompts is not None
        print("✓ Initialization successful")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False


def verify_pattern_extraction() -> bool:
    """Verify pattern extraction from grid."""
    print("\nTesting pattern extraction...")
    try:
        agent = WordGeneratorAgent()

        # Create empty grid
        grid = CrosswordGrid(size=8)

        # Create placement plan
        placement_plan = PlacementPlan(
            word="ATOM",
            clue="Smallest unit",
            start_row=0,
            start_col=0,
            direction="across",
            priority=0.9,
        )

        # Extract pattern
        pattern = agent.extract_pattern(grid, placement_plan)

        assert pattern is not None
        assert pattern.length == 4
        assert pattern.is_empty
        print(f"✓ Pattern extraction successful: {pattern}")
        return True
    except Exception as e:
        print(f"✗ Pattern extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_pattern_with_intersections() -> bool:
    """Verify pattern extraction with intersecting words."""
    print("\nTesting pattern extraction with intersections...")
    try:
        agent = WordGeneratorAgent()

        # Create grid with a word
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

        # Create placement plan that intersects
        placement_plan = PlacementPlan(
            word="IDEA",
            clue="Concept",
            start_row=0,
            start_col=2,
            direction="down",
            priority=0.8,
        )

        # Extract pattern
        pattern = agent.extract_pattern(grid, placement_plan)

        assert pattern is not None
        assert pattern.length == 4
        assert pattern.pattern[0] == "I"  # Intersects with SCIENCE
        assert not pattern.is_empty
        print(f"✓ Pattern with intersections: {pattern}")
        return True
    except Exception as e:
        print(f"✗ Pattern with intersections failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_constraint_extraction() -> bool:
    """Verify extraction of intersection constraints."""
    print("\nTesting constraint extraction...")
    try:
        agent = WordGeneratorAgent()

        # Create grid with a word
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

        # Create placement plan that intersects
        placement_plan = PlacementPlan(
            word="IDEA",
            clue="Concept",
            start_row=0,
            start_col=2,
            direction="down",
            priority=0.8,
        )

        # Get constraints
        constraints = agent.get_intersecting_constraints(grid, placement_plan)

        assert len(constraints) == 1
        assert constraints[0]["position"] == 0
        assert constraints[0]["letter"] == "I"
        assert constraints[0]["intersecting_word"] == "SCIENCE"
        print(f"✓ Constraint extraction successful: {constraints}")
        return True
    except Exception as e:
        print(f"✗ Constraint extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_prompt_generation() -> bool:
    """Verify prompt generation for word generation."""
    print("\nTesting prompt generation...")
    try:
        agent = WordGeneratorAgent()

        pattern = Pattern("A__M")

        # Generate system prompt
        system_prompt = agent.prompts.system_prompt()
        assert system_prompt is not None
        assert len(system_prompt) > 0
        assert "pattern" in system_prompt.lower()

        # Generate user prompt
        user_prompt = agent.prompts.user_prompt(
            topic="Science",
            pattern=pattern,
            difficulty="medium",
            direction="across",
            constraints=[],
            placed_words=["SCIENCE", "THEORY"],
        )
        assert user_prompt is not None
        assert len(user_prompt) > 0
        assert "Science" in user_prompt
        assert "A__M" in user_prompt

        print("✓ Prompt generation successful")
        return True
    except Exception as e:
        print(f"✗ Prompt generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_llm_response_parsing() -> bool:
    """Verify parsing of LLM responses."""
    print("\nTesting LLM response parsing...")
    try:
        agent = WordGeneratorAgent()

        # Valid response
        response = {
            "word": "ATOM",
            "clue": "Smallest unit of matter",
            "confidence": 0.9,
            "reasoning": "Good fit",
            "alternatives": ["CELL"],
        }
        pattern = Pattern("____")

        result = agent._parse_llm_response(response, pattern)
        assert result is not None
        assert result.word == "ATOM"
        assert result.clue == "Smallest unit of matter"
        assert result.confidence == 0.9

        # Invalid response (pattern mismatch)
        response_invalid = {
            "word": "TOOLONG",
            "clue": "Too long",
        }
        result_invalid = agent._parse_llm_response(response_invalid, pattern)
        assert result_invalid is None

        print("✓ LLM response parsing successful")
        return True
    except Exception as e:
        print(f"✗ LLM response parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_state_integration() -> bool:
    """Verify integration with AgentState."""
    print("\nTesting state integration...")
    try:
        agent = WordGeneratorAgent()

        # Create state
        requirements = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=8,
            max_words=15,
            difficulty="medium",
        )
        state = AgentState(requirements=requirements)

        # Initialize grid
        grid = CrosswordGrid(size=8)
        state.set_grid(grid)

        # Test should_continue
        should_continue = agent.should_continue(state)
        assert should_continue  # Should continue initially

        # Add enough words to meet requirements
        # Need to actually place words on grid, not just add to placed_words list
        grid = state.get_grid()
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
                state.add_placed_word(word)
        state.set_grid(grid)

        should_continue = agent.should_continue(state)
        assert not should_continue  # Should stop when requirements met

        print("✓ State integration successful")
        return True
    except Exception as e:
        print(f"✗ State integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_placement_plan_execution() -> bool:
    """Verify execution of placement plans."""
    print("\nTesting placement plan execution...")
    try:
        agent = WordGeneratorAgent()

        # Create state with empty placement plan
        requirements = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=8,
            max_words=15,
            difficulty="medium",
        )
        state = AgentState(requirements=requirements)
        state.set_grid(CrosswordGrid(size=8))

        # Test with empty plan
        count = agent.execute_placement_plan(state, max_placements=3)
        assert count == 0

        print("✓ Placement plan execution successful")
        return True
    except Exception as e:
        print(f"✗ Placement plan execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all verification tests."""
    print("=" * 60)
    print("WordGeneratorAgent Verification")
    print("=" * 60)

    tests = [
        verify_initialization,
        verify_pattern_extraction,
        verify_pattern_with_intersections,
        verify_constraint_extraction,
        verify_prompt_generation,
        verify_llm_response_parsing,
        verify_state_integration,
        verify_placement_plan_execution,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)

    if all(results):
        print("\n✓ All verification tests passed!")
        return 0
    else:
        print("\n✗ Some verification tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
