"""
Prompt templates for the PlannerAgent.

This module contains all prompt templates used by the PlannerAgent for
generating strategic word placement plans for crossword puzzles.
"""

from typing import Any


class PlannerPrompts:
    """
    Collection of prompt templates for the PlannerAgent.

    These prompts guide the LLM to generate strategic plans for crossword
    puzzle generation, including word selection, placement strategy, and
    intersection planning.
    """

    @staticmethod
    def system_prompt() -> str:
        """
        System prompt defining the PlannerAgent's role and responsibilities.

        Returns:
            System prompt string
        """
        return """You are an expert crossword puzzle planner with deep knowledge of puzzle construction principles. Your role is to create strategic plans for placing words on a crossword grid.

**Your Responsibilities:**
1. Analyze the current grid state and identify optimal placement opportunities
2. Generate thematically relevant words based on the given topic
3. Create a strategic placement plan that maximizes grid coverage and word intersections
4. Ensure words are appropriate for the specified difficulty level
5. Plan for good puzzle flow and solvability

**Crossword Construction Principles:**
- Start with longer words (6-10 letters) to establish the grid structure
- Place words to create multiple intersection points
- Ensure intersecting words share compatible letters
- Maintain good grid symmetry when possible
- Avoid isolated word clusters - aim for interconnected grid
- Consider letter frequency for better intersection possibilities (E, A, R, I, O, T, N, S are common)

**Word Selection Guidelines:**
- Easy: Common everyday words, direct definitions
- Medium: Mix of common and less common words, some wordplay
- Hard: Challenging vocabulary, cryptic clues, specialized terms

**Topic Relevance:**
- All words should relate to the given topic when possible
- Mix of direct topic words and tangentially related words
- Include variety: nouns, verbs, adjectives related to the topic

**Response Format:**
You must respond in JSON format with this exact structure:
{
    "action": "ADD_WORD",
    "reasoning": "Brief explanation of your strategy for this iteration",
    "word_candidates": [
        {
            "word": "EXAMPLE",
            "clue": "A representative case or instance",
            "priority": 0.9,
            "category": "general"
        }
    ],
    "placement_plan": [
        {
            "word": "EXAMPLE",
            "clue": "A representative case or instance",
            "start_row": 0,
            "start_col": 0,
            "direction": "across",
            "priority": 0.9,
            "reasoning": "Good starting word with common letters for intersections"
        }
    ]
}

**Important Notes:**
- Generate 3-8 word candidates per iteration
- Create placement plans for 1-3 words per iteration
- Priority ranges from 0.0 to 1.0 (higher = more important)
- Directions are "across" or "down"
- Start positions are 0-indexed (0,0 is top-left)
- **CRITICAL: Grid bounds validation**
  - For ACROSS words: start_col + word_length MUST be <= grid_size
  - For DOWN words: start_row + word_length MUST be <= grid_size
  - Example: In an 8x8 grid, a 4-letter ACROSS word starting at column 5 is INVALID (5+4=9 > 8)
  - Example: In an 8x8 grid, a 4-letter ACROSS word starting at column 4 is VALID (4+4=8 <= 8)
- Plan for intersections with existing words when grid is not empty"""

    @staticmethod
    def user_prompt(
        topic: str,
        grid_size: int,
        min_words: int,
        max_words: int,
        difficulty: str,
        grid_analysis: dict[str, Any],
    ) -> str:
        """
        User prompt for the PlannerAgent with current state information.

        Args:
            topic: Topic for puzzle generation
            grid_size: Size of the grid (NxN)
            min_words: Minimum number of words needed
            max_words: Maximum number of words allowed
            difficulty: Difficulty level (easy, medium, hard)
            grid_analysis: Current grid state analysis

        Returns:
            User prompt string
        """
        placed_words = grid_analysis.get("placed_words", [])
        fill_rate = grid_analysis.get("fill_rate", 0.0)
        word_count = grid_analysis.get("word_count", 0)
        iteration = grid_analysis.get("iteration", 0)
        available_spaces = grid_analysis.get("available_spaces", grid_size ** 2)
        intersections = grid_analysis.get("intersections", {})

        prompt = f"""Generate a strategic crossword puzzle plan for the topic: "{topic}"

**Puzzle Requirements:**
- Grid size: {grid_size}x{grid_size} (rows and columns are 0-indexed from 0 to {grid_size-1})
- Minimum words needed: {min_words}
- Maximum words allowed: {max_words}
- Difficulty level: {difficulty}
- Current iteration: {iteration + 1}

**CRITICAL GRID BOUNDS RULES:**
- Valid row indices: 0 to {grid_size-1}
- Valid column indices: 0 to {grid_size-1}
- For ACROSS words: start_col + word_length <= {grid_size}
- For DOWN words: start_row + word_length <= {grid_size}
- ALWAYS verify your placements fit within these bounds!

**Current Grid State:**
- Words placed: {word_count}
- Fill rate: {fill_rate:.1%}
- Available spaces: {available_spaces}
- Intersections: {intersections.get('count', 0)}
"""

        if placed_words:
            prompt += "\n**Words Already Placed:**\n"
            for word in placed_words:
                prompt += f"- {word}\n"

            prompt += f"""
**Strategy for This Iteration:**
Since words are already placed, focus on:
1. Finding words that intersect well with existing words
2. Filling gaps in the grid
3. Creating new intersection opportunities
4. Maintaining thematic relevance to "{topic}"
"""
        else:
            prompt += f"""
**Strategy for First Iteration:**
This is the first iteration. Focus on:
1. Selecting strong anchor words (6-10 letters) related to "{topic}"
2. Planning initial placements that allow for future intersections
3. Considering grid symmetry and balance
4. Using words with common letters (E, A, R, I, O, T, N, S) for better intersection potential
"""

        # Add difficulty-specific guidance
        if difficulty == "easy":
            prompt += """
**Difficulty Guidance (Easy):**
- Use common, everyday words
- Create straightforward, direct clues
- Avoid obscure vocabulary or specialized terms
- Aim for words that most people would know
"""
        elif difficulty == "medium":
            prompt += """
**Difficulty Guidance (Medium):**
- Mix of common and moderately challenging words
- Use some wordplay or indirect clues
- Include some less common but recognizable words
- Balance accessibility with challenge
"""
        else:  # hard
            prompt += """
**Difficulty Guidance (Hard):**
- Include challenging vocabulary
- Use cryptic or clever clues
- Consider specialized terms related to the topic
- Create clues that require lateral thinking
"""

        prompt += f"""
**Your Task:**
Generate {min(3, max_words - word_count)} word candidates with placement plans that:
1. Are thematically related to "{topic}"
2. Fit the {difficulty} difficulty level
3. Create good intersection opportunities
4. Fill the grid strategically
5. Are appropriate for the current grid state

Respond in the specified JSON format with word_candidates and placement_plan arrays."""

        return prompt

    @staticmethod
    def stop_prompt(
        topic: str,
        grid_analysis: dict[str, Any],
        requirements_met: bool,
    ) -> str:
        """
        Prompt for when the planner should consider stopping.

        Args:
            topic: Topic for puzzle generation
            grid_analysis: Current grid state analysis
            requirements_met: Whether minimum requirements are met

        Returns:
            User prompt string for stop decision
        """
        word_count = grid_analysis.get("word_count", 0)
        fill_rate = grid_analysis.get("fill_rate", 0.0)

        prompt = f"""Evaluate whether puzzle generation should stop for topic: "{topic}"

**Current State:**
- Words placed: {word_count}
- Fill rate: {fill_rate:.1%}
- Requirements met: {requirements_met}

**Decision Criteria:**
- If requirements are met and puzzle quality is good: STOP
- If grid is nearly full (>90%): STOP
- If no more good placement opportunities exist: STOP
- Otherwise: CONTINUE

Respond in JSON format:
{{
    "action": "STOP" or "ADD_WORD",
    "reasoning": "Explanation of decision",
    "stop_reason": "Reason for stopping (if applicable)"
}}"""

        return prompt


# Convenience instance
planner_prompts = PlannerPrompts()
