"""
Prompt templates for the WordGeneratorAgent.

This module contains all prompt templates used by the WordGeneratorAgent for
generating words that fit specific patterns in crossword puzzles.
"""

from typing import Any

from domain.pattern import Pattern


class WordGeneratorPrompts:
    """
    Collection of prompt templates for the WordGeneratorAgent.

    These prompts guide the LLM to generate words that fit specific patterns
    while maintaining thematic relevance and appropriate difficulty.
    """

    @staticmethod
    def system_prompt() -> str:
        """
        System prompt defining the WordGeneratorAgent's role and responsibilities.

        Returns:
            System prompt string
        """
        return """You are an expert crossword puzzle word generator with extensive vocabulary knowledge. Your role is to generate words that fit specific patterns while maintaining thematic relevance and appropriate difficulty.

**Your Responsibilities:**
1. Generate words that exactly match the given pattern (letters and underscores)
2. Ensure words are thematically related to the given topic
3. Create engaging, accurate clues for each word
4. Respect letter constraints from intersecting words
5. Match the specified difficulty level
6. Provide high-quality alternatives when possible

**Pattern Matching Rules:**
- Patterns use letters (A-Z) for known positions and underscores (_) for unknown positions
- Example: "A__LE" means a 5-letter word starting with 'A' and ending with 'LE'
- Your generated word MUST match the pattern exactly
- All letters must be uppercase A-Z (no spaces, hyphens, or special characters)

**Word Quality Guidelines:**
- Use real, valid English words (no proper nouns unless topic-specific)
- Prefer common words for easy difficulty, less common for medium, obscure for hard
- Ensure words are appropriate and family-friendly
- Avoid abbreviations, acronyms (unless topic-appropriate)
- Consider letter frequency for better crossword construction

**Clue Writing Guidelines:**
- Easy: Direct definitions, straightforward descriptions
- Medium: Some wordplay, indirect definitions, synonyms
- Hard: Cryptic clues, clever wordplay, lateral thinking required
- Clues should be concise but informative
- Avoid using the word itself in the clue
- Match clue difficulty to word difficulty

**Intersection Constraints:**
- When constraints are provided, the word MUST have the specified letters at those positions
- Constraints come from intersecting words already on the grid
- Violating constraints will cause placement failure

**Response Format:**
You must respond in JSON format with this exact structure:
{
    "word": "EXAMPLE",
    "clue": "A representative case or instance",
    "confidence": 0.9,
    "reasoning": "Common word that fits pattern and topic well",
    "alternatives": ["SAMPLE", "INSTANCE"]
}

**Field Descriptions:**
- word: The generated word (UPPERCASE, must match pattern exactly)
- clue: The crossword clue for this word
- confidence: Your confidence in this word choice (0.0 to 1.0)
- reasoning: Brief explanation of why this word is a good fit
- alternatives: 2-3 alternative words that also fit (optional)

**Important Notes:**
- ALWAYS verify your word matches the pattern before responding
- Consider the topic context when generating words
- Prioritize word quality over quantity
- If no good word fits, explain in reasoning and set confidence low"""

    @staticmethod
    def user_prompt(
        topic: str,
        pattern: Pattern,
        difficulty: str,
        direction: str,
        constraints: list[dict[str, Any]],
        placed_words: list[str],
    ) -> str:
        """
        User prompt for the WordGeneratorAgent with specific generation requirements.

        Args:
            topic: Topic for puzzle generation
            pattern: Pattern to match (e.g., "A__LE")
            difficulty: Difficulty level (easy, medium, hard)
            direction: Direction of word (across or down)
            constraints: List of intersection constraints
            placed_words: Words already placed on the grid

        Returns:
            User prompt string
        """
        prompt = f"""Generate a word for a crossword puzzle on the topic: "{topic}"

**Pattern Requirements:**
- Pattern: {pattern}
- Length: {pattern.length} letters
- Direction: {direction}
- Known positions: {len(pattern.known_positions)} out of {pattern.length}
"""

        # Add pattern details
        if pattern.known_positions:
            prompt += "\n**Known Letters:**\n"
            for pos, letter in pattern.known_positions.items():
                prompt += f"- Position {pos}: '{letter}'\n"
        else:
            prompt += "\n**Note:** All positions are unknown (pattern is all underscores)\n"

        # Add constraints from intersecting words
        if constraints:
            prompt += "\n**Intersection Constraints:**\n"
            prompt += f"This word intersects with {len(constraints)} existing word(s):\n"
            for constraint in constraints:
                prompt += (
                    f"- Position {constraint['position']}: must be '{constraint['letter']}' "
                    f"(intersects with '{constraint['intersecting_word']}')\n"
                )
            prompt += "\n**CRITICAL:** Your word MUST have these exact letters at these positions!\n"

        # Add context about placed words
        if placed_words:
            prompt += f"\n**Words Already Placed ({len(placed_words)}):**\n"
            # Show up to 10 words for context
            display_words = placed_words[:10]
            for word in display_words:
                prompt += f"- {word}\n"
            if len(placed_words) > 10:
                prompt += f"... and {len(placed_words) - 10} more\n"
            prompt += "\n**Note:** Try to avoid repeating these words or their roots\n"

        # Add difficulty-specific guidance
        prompt += f"\n**Difficulty Level: {difficulty.upper()}**\n"

        if difficulty == "easy":
            prompt += """
**Word Selection for Easy:**
- Use common, everyday words that most people know
- Prefer words with 4-8 letters
- Choose words with straightforward meanings
- Examples: APPLE, HOUSE, WATER, FRIEND

**Clue Writing for Easy:**
- Use direct definitions
- Be clear and unambiguous
- Example: "Red fruit" for APPLE
"""
        elif difficulty == "medium":
            prompt += """
**Word Selection for Medium:**
- Mix of common and moderately challenging words
- Can use words with 5-10 letters
- Include some less common but recognizable words
- Examples: QUANTUM, ECLIPSE, GLACIER, THEOREM

**Clue Writing for Medium:**
- Use indirect definitions or synonyms
- Include some wordplay or double meanings
- Example: "Frozen river of ice" for GLACIER
"""
        else:  # hard
            prompt += """
**Word Selection for Hard:**
- Include challenging vocabulary
- Can use specialized or technical terms
- Words with 6-12 letters acceptable
- Examples: QUIXOTIC, EPHEMERAL, PARADIGM, ZEITGEIST

**Clue Writing for Hard:**
- Use cryptic or clever clues
- Employ wordplay, puns, or lateral thinking
- Example: "Impractically idealistic" for QUIXOTIC
"""

        # Add topic-specific guidance
        prompt += f"""
**Topic Relevance: "{topic}"**
Your word should be related to this topic. Consider:
- Direct topic words (e.g., for "Science": ATOM, THEORY, EXPERIMENT)
- Related concepts (e.g., for "Science": DISCOVERY, RESEARCH, LABORATORY)
- Associated terms (e.g., for "Science": EINSTEIN, NEWTON, HYPOTHESIS)

**Your Task:**
Generate ONE word that:
1. EXACTLY matches the pattern: {pattern}
2. Fits ALL intersection constraints (if any)
3. Is related to the topic: "{topic}"
4. Matches the {difficulty} difficulty level
5. Has an appropriate, well-crafted clue
6. Is a valid English word (no proper nouns unless topic-specific)

**Verification Checklist:**
Before responding, verify:
✓ Word length matches pattern length ({pattern.length} letters)
✓ Word has correct letters at known positions
✓ Word satisfies all intersection constraints
✓ Word is related to topic "{topic}"
✓ Word is appropriate for {difficulty} difficulty
✓ Clue is well-written and doesn't contain the word
✓ Word is uppercase letters only (A-Z)

Respond in the specified JSON format with word, clue, confidence, reasoning, and alternatives.
"""

        return prompt

    @staticmethod
    def retry_prompt(
        previous_word: str,
        rejection_reason: str,
        pattern: Pattern,
        topic: str,
    ) -> str:
        """
        Prompt for retrying word generation after a failure.

        Args:
            previous_word: Word that was rejected
            rejection_reason: Reason for rejection
            pattern: Pattern to match
            topic: Topic for puzzle generation

        Returns:
            User prompt string for retry
        """
        prompt = f"""The previous word "{previous_word}" was rejected.

**Rejection Reason:**
{rejection_reason}

**Requirements (unchanged):**
- Pattern: {pattern}
- Topic: "{topic}"

**Your Task:**
Generate a DIFFERENT word that:
1. Matches the pattern exactly
2. Avoids the issues that caused rejection
3. Is still related to the topic
4. Is a valid alternative

Please provide a new word with its clue, ensuring it addresses the rejection reason.

Respond in the specified JSON format.
"""
        return prompt

    @staticmethod
    def alternative_prompt(
        primary_word: str,
        pattern: Pattern,
        topic: str,
        count: int = 3,
    ) -> str:
        """
        Prompt for generating alternative words.

        Args:
            primary_word: Primary word already generated
            pattern: Pattern to match
            topic: Topic for puzzle generation
            count: Number of alternatives to generate

        Returns:
            User prompt string for alternatives
        """
        prompt = f"""Generate {count} alternative words for the pattern: {pattern}

**Context:**
- Primary word: {primary_word}
- Topic: "{topic}"
- Pattern: {pattern}

**Your Task:**
Provide {count} different words that:
1. Match the same pattern
2. Are related to the same topic
3. Are distinct from the primary word
4. Are valid alternatives

Respond with a JSON array of word objects:
[
    {{"word": "WORD1", "clue": "Clue for word 1"}},
    {{"word": "WORD2", "clue": "Clue for word 2"}},
    {{"word": "WORD3", "clue": "Clue for word 3"}}
]
"""
        return prompt


# Convenience instance
word_generator_prompts = WordGeneratorPrompts()
