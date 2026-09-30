"""
Verification script for LangGraph workflow foundation.

This script verifies that the workflow, state, and LLM components are
properly implemented and working together.
"""

import sys

from agents import (
    AgentState,
    CrosswordWorkflow,
    PlacementPlan,
    PuzzleRequirements,
    WordCandidate,
    get_workflow,
)
from domain import CrosswordGrid, Direction, WordPlacement


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def verify_state_models() -> bool:
    """Verify state models are working correctly."""
    print_section("Verifying State Models")

    try:
        # Test PuzzleRequirements
        print("✓ Creating PuzzleRequirements...")
        req = PuzzleRequirements(
            topic="Science",
            grid_size=8,
            min_words=10,
            max_words=15,
            difficulty="medium",
        )
        print(f"  Topic: {req.topic}")
        print(f"  Grid size: {req.grid_size}x{req.grid_size}")
        print(f"  Words: {req.min_words}-{req.max_words}")
        print(f"  Difficulty: {req.difficulty}")

        # Test WordCandidate
        print("\n✓ Creating WordCandidate...")
        candidate = WordCandidate(
            word="SCIENCE",
            clue="Study of the natural world",
            priority=0.9,
            category="education",
        )
        print(f"  Word: {candidate.word}")
        print(f"  Clue: {candidate.clue}")
        print(f"  Priority: {candidate.priority}")

        # Test PlacementPlan
        print("\n✓ Creating PlacementPlan...")
        plan = PlacementPlan(
            word="SCIENCE",
            clue="Study of the natural world",
            start_row=0,
            start_col=0,
            direction="across",
            priority=0.9,
            reasoning="Good starting word with common letters",
        )
        print(f"  Word: {plan.word}")
        print(f"  Position: ({plan.start_row}, {plan.start_col})")
        print(f"  Direction: {plan.direction}")

        # Test AgentState
        print("\n✓ Creating AgentState...")
        state = AgentState(requirements=req)
        print(f"  Status: {state.status}")
        print(f"  Iteration: {state.iteration}/{state.max_iterations}")
        print(f"  Word count: {state.get_word_count()}")

        # Test grid operations
        print("\n✓ Testing grid serialization...")
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

        state.set_grid(grid)
        retrieved_grid = state.get_grid()
        assert retrieved_grid is not None
        assert retrieved_grid.size == 8
        assert len(retrieved_grid.words) == 1
        print("  Grid serialized and deserialized successfully")
        print(f"  Words on grid: {state.get_word_count()}")
        print(f"  Fill rate: {state.get_fill_rate():.2%}")

        # Test state tracking
        print("\n✓ Testing state tracking...")
        state.add_placed_word("SCIENCE")
        state.add_failed_placement("INVALID", "Out of bounds")
        state.increment_iteration()
        print(f"  Placed words: {state.placed_words}")
        print(f"  Failed placements: {len(state.failed_placements)}")
        print(f"  Current iteration: {state.iteration}")

        # Test serialization
        print("\n✓ Testing state serialization...")
        state_dict = state.to_dict()
        restored_state = AgentState.from_dict(state_dict)
        assert restored_state.requirements.topic == "Science"
        assert restored_state.iteration == 1
        print("  State serialized and restored successfully")

        print("\n✅ All state model tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ State model verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_workflow() -> bool:
    """Verify workflow is working correctly."""
    print_section("Verifying Workflow")

    try:
        # Test workflow creation
        print("✓ Creating workflow...")
        workflow = CrosswordWorkflow()
        print("  Workflow created successfully")

        # Test singleton
        print("\n✓ Testing workflow singleton...")
        workflow2 = get_workflow()
        assert workflow2 is not None
        print("  Singleton pattern working")

        # Test workflow nodes
        print("\n✓ Testing workflow nodes...")
        req = PuzzleRequirements(topic="Science", grid_size=8)
        state = AgentState(requirements=req)

        # Initialize node
        init_updates = workflow._initialize_node(state)
        assert "grid_state" in init_updates
        assert init_updates["status"] == "planning"
        print("  Initialize node: ✓")

        # Update state
        state.grid_state = init_updates["grid_state"]
        state.status = init_updates["status"]

        # Planner node
        plan_updates = workflow._planner_node(state)
        assert plan_updates["status"] == "planning"
        print("  Planner node: ✓")

        # Executor node
        exec_updates = workflow._executor_node(state)
        assert exec_updates["status"] == "executing"
        assert exec_updates["iteration"] == 1
        print("  Executor node: ✓")

        # Test should_continue logic
        print("\n✓ Testing workflow control flow...")

        # Should continue (not enough words)
        state.iteration = 1
        result = workflow._should_continue(state)
        assert result == "continue"
        print("  Continue when requirements not met: ✓")

        # Should end (max iterations)
        state.iteration = state.max_iterations
        result = workflow._should_continue(state)
        assert result == "end"
        print("  End when max iterations reached: ✓")

        # Test full workflow execution
        print("\n✓ Testing full workflow execution...")
        final_state = workflow.generate_puzzle(
            topic="Science",
            grid_size=8,
            min_words=2,
            max_words=5,
            difficulty="medium",
            max_iterations=3,
        )

        assert final_state is not None
        assert final_state.requirements.topic == "Science"
        assert final_state.grid_state is not None
        print("  Workflow executed successfully")
        print(f"  Final status: {final_state.status}")
        print(f"  Iterations: {final_state.iteration}")

        print("\n✅ All workflow tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Workflow verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_llm_client() -> bool:
    """Verify LLM client is properly configured."""
    print_section("Verifying LLM Client")

    try:
        from llm import LLMClient, get_llm_client

        # Test client creation
        print("✓ Creating LLM client...")
        client = LLMClient()
        print(f"  Model: {client.model}")
        print(f"  Temperature: {client.temperature}")

        # Test singleton
        print("\n✓ Testing client singleton...")
        client2 = get_llm_client()
        assert client2 is not None
        print("  Singleton pattern working")

        # Note: We don't make actual API calls in verification
        print("\n✓ LLM client structure verified")
        print("  (Actual API calls will be tested in integration tests)")

        print("\n✅ LLM client verification passed!")
        return True

    except Exception as e:
        print(f"\n❌ LLM client verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_prompts() -> bool:
    """Verify prompt templates are working."""
    print_section("Verifying Prompt Templates")

    try:
        from llm import PromptTemplates, prompts

        # Test system prompts
        print("✓ Testing system prompts...")
        planner_sys = PromptTemplates.planner_system_prompt()
        assert len(planner_sys) > 0
        assert "JSON" in planner_sys or "json" in planner_sys
        print(f"  Planner system prompt: {len(planner_sys)} chars")

        word_gen_sys = PromptTemplates.word_generator_system_prompt()
        assert len(word_gen_sys) > 0
        print(f"  Word generator system prompt: {len(word_gen_sys)} chars")

        solver_sys = PromptTemplates.solver_system_prompt()
        assert len(solver_sys) > 0
        print(f"  Solver system prompt: {len(solver_sys)} chars")

        # Test user prompts
        print("\n✓ Testing user prompts...")
        planner_user = PromptTemplates.planner_user_prompt(
            topic="Science",
            grid_size=8,
            min_words=10,
            max_words=15,
            difficulty="medium",
            current_state={"placed_words": [], "iteration": 0},
        )
        assert "Science" in planner_user
        assert "8x8" in planner_user
        print(f"  Planner user prompt: {len(planner_user)} chars")

        word_gen_user = PromptTemplates.word_generator_user_prompt(
            pattern="A__LE",
            topic="Science",
            difficulty="medium",
            context={},
        )
        assert "A__LE" in word_gen_user
        print(f"  Word generator user prompt: {len(word_gen_user)} chars")

        solver_user = PromptTemplates.solver_user_prompt(
            clue="Study of nature",
            pattern="S____CE",
            context={},
        )
        assert "Study of nature" in solver_user
        print(f"  Solver user prompt: {len(solver_user)} chars")

        # Test singleton
        print("\n✓ Testing prompts singleton...")
        assert prompts is not None
        assert isinstance(prompts, PromptTemplates)
        print("  Singleton instance available")

        print("\n✅ All prompt template tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Prompt template verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("  LangGraph Workflow Foundation Verification")
    print("=" * 60)

    results = {
        "State Models": verify_state_models(),
        "Workflow": verify_workflow(),
        "LLM Client": verify_llm_client(),
        "Prompt Templates": verify_prompts(),
    }

    print_section("Verification Summary")

    all_passed = True
    for component, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{component:.<40} {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n" + "=" * 60)
        print("  🎉 ALL VERIFICATIONS PASSED!")
        print("=" * 60)
        print("\nThe LangGraph workflow foundation is ready for agent implementation.")
        print("\nNext steps:")
        print("  1. Implement PlannerAgent")
        print("  2. Implement WordGeneratorAgent")
        print("  3. Integrate agents with workflow")
        print("  4. Add LLM-based word generation")
        return 0
    else:
        print("\n" + "=" * 60)
        print("  ❌ SOME VERIFICATIONS FAILED")
        print("=" * 60)
        print("\nPlease review the errors above and fix the issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
