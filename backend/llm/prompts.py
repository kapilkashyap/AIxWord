"""
Prompt templates for LLM interactions.

This module contains all prompt templates used by the agents for generating
crossword puzzles, clues, and solving assistance.
"""

from typing import Any


class PromptTemplates:
    """
    Collection of prompt templates for crossword puzzle generation and solving.

    All prompts are designed to work with OpenAI's chat completion API
    and support JSON mode for structured outputs.
    """

    @staticmethod
    def planner_system_prompt() -> str:
        """
        System prompt for the PlannerAgent.

        Returns:
            System prompt string
        """
        return """You are an expert crossword puzzle planner. Your role is to:

1. Analyze the given topic and generate relevant words for a crossword puzzle
2. Create a strategic plan for placing words on the grid
3. Ensure words are thematically related to the topic
4. Prioritize words that will create good intersections
5. Consider difficulty level when selecting words

Guidelines:
- Generate words of varying lengths (3-10 letters preferred)
- Ensure words are common enough to be solvable
- Create interesting and fair clues
- Plan for good grid coverage and interconnection
- Avoid obscure or overly technical terms unless appropriate for the topic

You must respond in JSON format with the following structure:
{
    "word_candidates": [
        {
            "word": "EXAMPLE",
            "clue": "A representative case",
            "priority": 0.9,
            "category": "general"
        }
    ],
    "placement_plan": [
        {
            "word": "EXAMPLE",
            "clue": "A representative case",
            "start_row": 0,
            "start_col": 0,
            "direction": "across",
            "priority": 0.9,
            "reasoning": "Good starting word with common letters"
        }
    ],
    "strategy": "Overall strategy explanation"
}"""

    @staticmethod
    def planner_user_prompt(
        topic: str,
        grid_size: int,
        min_words: int,
        max_words: int,
        difficulty: str,
        current_state: dict[str, Any],
    ) -> str:
        """
        User prompt for the PlannerAgent.

        Args:
            topic: Topic for puzzle generation
            grid_size: Size of the grid (NxN)
            min_words: Minimum number of words needed
            max_words: Maximum number of words allowed
            difficulty: Difficulty level (easy, medium, hard)
            current_state: Current state of the puzzle (grid, placed words, etc.)

        Returns:
            User prompt string
        """
        placed_words = current_state.get("placed_words", [])
        iteration = current_state.get("iteration", 0)

        prompt = f"""Generate a crossword puzzle plan for the topic: "{topic}"

Requirements:
- Grid size: {grid_size}x{grid_size}
- Minimum words: {min_words}
- Maximum words: {max_words}
- Difficulty: {difficulty}
- Current iteration: {iteration}
"""

        if placed_words:
            prompt += f"\nWords already placed: {', '.join(placed_words)}"
            prompt += "\nPlan additional words that will intersect well with existing words."
        else:
            prompt += "\nThis is the first iteration. Plan the initial set of words."

        prompt += """

Generate word candidates and a placement plan. Consider:
1. Thematic relevance to the topic
2. Word length variety
3. Potential for good intersections
4. Appropriate difficulty level
5. Grid coverage and balance

Respond in the specified JSON format."""

        return prompt

    @staticmethod
    def word_generator_system_prompt() -> str:
        """
        System prompt for the WordGeneratorAgent.

        Returns:
            System prompt string
        """
        return """You are an expert crossword puzzle word generator. Your role is to:

1. Generate words that fit specific patterns (e.g., "A__LE" for 5-letter words starting with A and ending with LE)
2. Create appropriate clues for generated words
3. Ensure words are valid and appropriate for crossword puzzles
4. Consider the topic and difficulty level

Guidelines:
- Generate common, solvable words
- Avoid proper nouns unless specifically requested
- Create clear, fair clues
- Ensure words match the required pattern exactly
- Consider letter frequency for better intersections

You must respond in JSON format with the following structure:
{
    "word": "APPLE",
    "clue": "A common fruit",
    "confidence": 0.95,
    "alternatives": [
        {
            "word": "ANKLE",
            "clue": "Joint between foot and leg",
            "confidence": 0.85
        }
    ]
}"""

    @staticmethod
    def word_generator_user_prompt(
        pattern: str,
        topic: str,
        difficulty: str,
        context: dict[str, Any],
    ) -> str:
        """
        User prompt for the WordGeneratorAgent.

        Args:
            pattern: Pattern to match (e.g., "A__LE" where _ is unknown)
            topic: Topic for the puzzle
            difficulty: Difficulty level
            context: Additional context (intersecting words, etc.)

        Returns:
            User prompt string
        """
        prompt = f"""Generate a word that matches the pattern: "{pattern}"

Requirements:
- Topic: {topic}
- Difficulty: {difficulty}
- Pattern: {pattern} (where _ represents any letter)
"""

        if context.get("intersecting_words"):
            prompt += f"\nIntersecting words: {', '.join(context['intersecting_words'])}"

        if context.get("direction"):
            prompt += f"\nDirection: {context['direction']}"

        prompt += """

Generate a word that:
1. Matches the pattern exactly
2. Is thematically related to the topic
3. Is appropriate for the difficulty level
4. Would make a good crossword puzzle word

Also provide 2-3 alternative words if possible.
Respond in the specified JSON format."""

        return prompt

    @staticmethod
    def clue_generator_system_prompt() -> str:
        """
        System prompt for clue generation.

        Returns:
            System prompt string
        """
        return """You are an expert crossword puzzle clue writer. Your role is to:

1. Create clear, fair, and interesting clues
2. Match clue difficulty to the specified level
3. Avoid ambiguous or misleading clues
4. Use appropriate crossword conventions

Guidelines:
- Easy: Direct definitions or common associations
- Medium: Wordplay, synonyms, or indirect references
- Hard: Cryptic clues, obscure references, or complex wordplay

You must respond in JSON format with the following structure:
{
    "clue": "The main clue text",
    "alternatives": [
        "Alternative clue 1",
        "Alternative clue 2"
    ],
    "difficulty_rating": 0.7
}"""

    @staticmethod
    def clue_generator_user_prompt(
        word: str,
        topic: str,
        difficulty: str,
        context: dict[str, Any],
    ) -> str:
        """
        User prompt for clue generation.

        Args:
            word: Word to create clue for
            topic: Topic of the puzzle
            difficulty: Difficulty level
            context: Additional context

        Returns:
            User prompt string
        """
        prompt = f"""Generate a crossword clue for the word: "{word}"

Requirements:
- Topic: {topic}
- Difficulty: {difficulty}
- Word length: {len(word)} letters
"""

        if context.get("category"):
            prompt += f"\nCategory: {context['category']}"

        prompt += """

Create a clue that:
1. Is appropriate for the difficulty level
2. Relates to the topic when possible
3. Is clear and fair
4. Follows crossword conventions

Provide the main clue and 2-3 alternatives.
Respond in the specified JSON format."""

        return prompt

    @staticmethod
    def solver_system_prompt() -> str:
        """
        System prompt for puzzle solving assistance.

        Returns:
            System prompt string
        """
        return """You are an expert crossword puzzle solver. Your role is to:

1. Solve crossword clues accurately
2. Consider the pattern (known letters) when solving
3. Provide confidence scores for your answers
4. Offer alternative solutions when appropriate

Guidelines:
- Use the pattern to narrow down possibilities
- Consider common crossword conventions
- Provide clear reasoning for your answers
- Offer multiple solutions when uncertain

You must respond in JSON format with the following structure:
{
    "answer": "SOLUTION",
    "confidence": 0.95,
    "reasoning": "Explanation of the answer",
    "alternatives": [
        {
            "answer": "ALTERNATE",
            "confidence": 0.75,
            "reasoning": "Alternative explanation"
        }
    ]
}"""

    @staticmethod
    def solver_user_prompt(
        clue: str,
        pattern: str,
        context: dict[str, Any],
    ) -> str:
        """
        User prompt for puzzle solving.

        Args:
            clue: The crossword clue
            pattern: Pattern with known letters (e.g., "A__LE")
            context: Additional context

        Returns:
            User prompt string
        """
        prompt = f"""Solve this crossword clue:

Clue: "{clue}"
Pattern: "{pattern}" (where _ represents unknown letters)
Length: {len(pattern)} letters
"""

        if context.get("topic"):
            prompt += f"\nPuzzle topic: {context['topic']}"

        if context.get("intersecting_words"):
            prompt += f"\nIntersecting words: {', '.join(context['intersecting_words'])}"

        prompt += """

Provide:
1. Your best answer that matches the pattern
2. Confidence score (0.0 to 1.0)
3. Reasoning for your answer
4. Alternative solutions if applicable

Respond in the specified JSON format."""

        return prompt

    @staticmethod
    def hint_generator_system_prompt() -> str:
        """
        System prompt for hint generation.

        Returns:
            System prompt string
        """
        return """You are a helpful crossword puzzle hint provider. Your role is to:

1. Provide helpful hints without giving away the answer
2. Offer progressively more revealing hints
3. Maintain the challenge and fun of solving

Guidelines:
- Start with subtle hints
- Provide category or theme hints
- Offer letter position hints if needed
- Never reveal the full answer directly

You must respond in JSON format with the following structure:
{
    "hints": [
        {
            "level": 1,
            "text": "Subtle hint",
            "reveals": "category"
        },
        {
            "level": 2,
            "text": "More specific hint",
            "reveals": "first_letter"
        },
        {
            "level": 3,
            "text": "Very specific hint",
            "reveals": "multiple_letters"
        }
    ]
}"""

    @staticmethod
    def hint_generator_user_prompt(
        clue: str,
        answer: str,
        pattern: str,
        context: dict[str, Any],
    ) -> str:
        """
        User prompt for hint generation.

        Args:
            clue: The crossword clue
            answer: The correct answer
            pattern: Current pattern with known letters
            context: Additional context

        Returns:
            User prompt string
        """
        prompt = f"""Generate progressive hints for this crossword clue:

Clue: "{clue}"
Answer: "{answer}"
Current pattern: "{pattern}"
"""

        if context.get("topic"):
            prompt += f"\nPuzzle topic: {context['topic']}"

        prompt += """

Generate 3 levels of hints:
1. Level 1: Subtle hint (category, theme, or general direction)
2. Level 2: More specific hint (first letter, word type, or partial info)
3. Level 3: Very specific hint (multiple letters or strong clue)

Each hint should be helpful but maintain the challenge.
Respond in the specified JSON format."""

        return prompt


# Convenience instance
prompts = PromptTemplates()
