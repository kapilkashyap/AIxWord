"""
Tests for prompt templates.

This module tests the PromptTemplates class and prompt generation.
"""


from backend.llm.prompts import PromptTemplates, prompts


class TestPromptTemplates:
    """Tests for PromptTemplates class."""

    def test_planner_system_prompt(self) -> None:
        """Test planner system prompt generation."""
        prompt = PromptTemplates.planner_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "crossword" in prompt.lower()
        assert "JSON" in prompt or "json" in prompt
        assert "word_candidates" in prompt
        assert "placement_plan" in prompt

    def test_planner_user_prompt_initial(self) -> None:
        """Test planner user prompt for initial iteration."""
        prompt = PromptTemplates.planner_user_prompt(
            topic="Science",
            grid_size=8,
            min_words=10,
            max_words=15,
            difficulty="medium",
            current_state={"placed_words": [], "iteration": 0},
        )

        assert isinstance(prompt, str)
        assert "Science" in prompt
        assert "8x8" in prompt
        assert "10" in prompt  # min_words
        assert "15" in prompt  # max_words
        assert "medium" in prompt
        assert "first iteration" in prompt.lower()

    def test_planner_user_prompt_with_placed_words(self) -> None:
        """Test planner user prompt with existing words."""
        prompt = PromptTemplates.planner_user_prompt(
            topic="History",
            grid_size=8,
            min_words=10,
            max_words=15,
            difficulty="hard",
            current_state={
                "placed_words": ["SCIENCE", "HISTORY"],
                "iteration": 2,
            },
        )

        assert "History" in prompt
        assert "SCIENCE" in prompt
        assert "HISTORY" in prompt
        assert "iteration: 2" in prompt.lower() or "2" in prompt
        assert "intersect" in prompt.lower()

    def test_word_generator_system_prompt(self) -> None:
        """Test word generator system prompt."""
        prompt = PromptTemplates.word_generator_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "pattern" in prompt.lower()
        assert "JSON" in prompt or "json" in prompt
        assert "word" in prompt.lower()
        assert "clue" in prompt.lower()
        assert "confidence" in prompt.lower()

    def test_word_generator_user_prompt_basic(self) -> None:
        """Test word generator user prompt with basic parameters."""
        prompt = PromptTemplates.word_generator_user_prompt(
            pattern="A__LE",
            topic="Science",
            difficulty="medium",
            context={},
        )

        assert "A__LE" in prompt
        assert "Science" in prompt
        assert "medium" in prompt
        assert "pattern" in prompt.lower()

    def test_word_generator_user_prompt_with_context(self) -> None:
        """Test word generator user prompt with context."""
        prompt = PromptTemplates.word_generator_user_prompt(
            pattern="S____E",
            topic="Science",
            difficulty="hard",
            context={
                "intersecting_words": ["PHYSICS", "BIOLOGY"],
                "direction": "across",
            },
        )

        assert "S____E" in prompt
        assert "PHYSICS" in prompt
        assert "BIOLOGY" in prompt
        assert "across" in prompt.lower()

    def test_clue_generator_system_prompt(self) -> None:
        """Test clue generator system prompt."""
        prompt = PromptTemplates.clue_generator_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "clue" in prompt.lower()
        assert "difficulty" in prompt.lower()
        assert "JSON" in prompt or "json" in prompt

    def test_clue_generator_user_prompt_basic(self) -> None:
        """Test clue generator user prompt."""
        prompt = PromptTemplates.clue_generator_user_prompt(
            word="SCIENCE",
            topic="Education",
            difficulty="easy",
            context={},
        )

        assert "SCIENCE" in prompt
        assert "Education" in prompt
        assert "easy" in prompt
        assert "7 letters" in prompt or "7" in prompt

    def test_clue_generator_user_prompt_with_category(self) -> None:
        """Test clue generator user prompt with category."""
        prompt = PromptTemplates.clue_generator_user_prompt(
            word="PHYSICS",
            topic="Science",
            difficulty="medium",
            context={"category": "natural science"},
        )

        assert "PHYSICS" in prompt
        assert "natural science" in prompt

    def test_solver_system_prompt(self) -> None:
        """Test solver system prompt."""
        prompt = PromptTemplates.solver_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "solve" in prompt.lower()
        assert "pattern" in prompt.lower()
        assert "confidence" in prompt.lower()
        assert "JSON" in prompt or "json" in prompt

    def test_solver_user_prompt_basic(self) -> None:
        """Test solver user prompt."""
        prompt = PromptTemplates.solver_user_prompt(
            clue="Study of the natural world",
            pattern="S____CE",
            context={},
        )

        assert "Study of the natural world" in prompt
        assert "S____CE" in prompt
        assert "7 letters" in prompt or "7" in prompt

    def test_solver_user_prompt_with_context(self) -> None:
        """Test solver user prompt with context."""
        prompt = PromptTemplates.solver_user_prompt(
            clue="Past events",
            pattern="H_ST__Y",
            context={
                "topic": "Education",
                "intersecting_words": ["SCIENCE"],
            },
        )

        assert "Past events" in prompt
        assert "H_ST__Y" in prompt
        assert "Education" in prompt
        assert "SCIENCE" in prompt

    def test_hint_generator_system_prompt(self) -> None:
        """Test hint generator system prompt."""
        prompt = PromptTemplates.hint_generator_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "hint" in prompt.lower()
        assert "level" in prompt.lower()
        assert "JSON" in prompt or "json" in prompt

    def test_hint_generator_user_prompt_basic(self) -> None:
        """Test hint generator user prompt."""
        prompt = PromptTemplates.hint_generator_user_prompt(
            clue="Study of the natural world",
            answer="SCIENCE",
            pattern="_______",
            context={},
        )

        assert "Study of the natural world" in prompt
        assert "SCIENCE" in prompt
        assert "_______" in prompt
        assert "3 levels" in prompt.lower() or "level" in prompt.lower()

    def test_hint_generator_user_prompt_with_topic(self) -> None:
        """Test hint generator user prompt with topic."""
        prompt = PromptTemplates.hint_generator_user_prompt(
            clue="Past events",
            answer="HISTORY",
            pattern="H______",
            context={"topic": "Education"},
        )

        assert "Past events" in prompt
        assert "HISTORY" in prompt
        assert "H______" in prompt
        assert "Education" in prompt

    def test_prompts_singleton(self) -> None:
        """Test prompts singleton instance."""
        assert prompts is not None
        assert isinstance(prompts, PromptTemplates)

    def test_all_prompts_return_strings(self) -> None:
        """Test that all prompt methods return non-empty strings."""
        # System prompts
        assert isinstance(PromptTemplates.planner_system_prompt(), str)
        assert isinstance(PromptTemplates.word_generator_system_prompt(), str)
        assert isinstance(PromptTemplates.clue_generator_system_prompt(), str)
        assert isinstance(PromptTemplates.solver_system_prompt(), str)
        assert isinstance(PromptTemplates.hint_generator_system_prompt(), str)

        # User prompts with minimal parameters
        assert isinstance(
            PromptTemplates.planner_user_prompt(
                "Test", 8, 5, 10, "medium", {}
            ),
            str,
        )
        assert isinstance(
            PromptTemplates.word_generator_user_prompt(
                "A__LE", "Test", "medium", {}
            ),
            str,
        )
        assert isinstance(
            PromptTemplates.clue_generator_user_prompt(
                "TEST", "Test", "medium", {}
            ),
            str,
        )
        assert isinstance(
            PromptTemplates.solver_user_prompt("Test clue", "____", {}),
            str,
        )
        assert isinstance(
            PromptTemplates.hint_generator_user_prompt(
                "Test clue", "TEST", "____", {}
            ),
            str,
        )

    def test_prompt_contains_json_instructions(self) -> None:
        """Test that prompts contain JSON format instructions."""
        system_prompts = [
            PromptTemplates.planner_system_prompt(),
            PromptTemplates.word_generator_system_prompt(),
            PromptTemplates.clue_generator_system_prompt(),
            PromptTemplates.solver_system_prompt(),
            PromptTemplates.hint_generator_system_prompt(),
        ]

        for prompt in system_prompts:
            assert "JSON" in prompt or "json" in prompt

    def test_planner_prompt_structure(self) -> None:
        """Test planner prompt has expected structure."""
        system_prompt = PromptTemplates.planner_system_prompt()

        # Should mention key fields
        assert "word_candidates" in system_prompt
        assert "placement_plan" in system_prompt
        assert "word" in system_prompt
        assert "clue" in system_prompt
        assert "priority" in system_prompt
        assert "direction" in system_prompt

    def test_word_generator_prompt_structure(self) -> None:
        """Test word generator prompt has expected structure."""
        system_prompt = PromptTemplates.word_generator_system_prompt()

        # Should mention key fields
        assert "word" in system_prompt
        assert "clue" in system_prompt
        assert "confidence" in system_prompt
        assert "alternatives" in system_prompt

    def test_solver_prompt_structure(self) -> None:
        """Test solver prompt has expected structure."""
        system_prompt = PromptTemplates.solver_system_prompt()

        # Should mention key fields
        assert "answer" in system_prompt
        assert "confidence" in system_prompt
        assert "reasoning" in system_prompt
        assert "alternatives" in system_prompt

    def test_hint_prompt_structure(self) -> None:
        """Test hint prompt has expected structure."""
        system_prompt = PromptTemplates.hint_generator_system_prompt()

        # Should mention key fields
        assert "hints" in system_prompt
        assert "level" in system_prompt
        assert "text" in system_prompt

    def test_difficulty_levels_in_prompts(self) -> None:
        """Test that difficulty levels are properly included."""
        for difficulty in ["easy", "medium", "hard"]:
            prompt = PromptTemplates.planner_user_prompt(
                "Test", 8, 5, 10, difficulty, {}
            )
            assert difficulty in prompt

    def test_pattern_format_in_prompts(self) -> None:
        """Test that pattern format is explained in prompts."""
        prompt = PromptTemplates.word_generator_user_prompt(
            "A__LE", "Test", "medium", {}
        )

        # Should explain that _ represents unknown letters
        assert "_" in prompt
        assert "unknown" in prompt.lower() or "any" in prompt.lower()
