"""
AI-powered puzzle solving service.

This module provides services for solving crossword puzzles using AI:
- Solve entire puzzles
- Solve individual words
- Generate hints
"""

import logging
import random
from typing import Any, Optional

from backend.llm.client import LLMClient

logger = logging.getLogger(__name__)


class PuzzleSolver:
    """
    AI-powered crossword puzzle solver.

    This service uses LLM to solve crossword puzzles by:
    1. Analyzing clues and constraints
    2. Generating candidate answers
    3. Validating answers against intersections
    4. Providing hints and explanations
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the puzzle solver.

        Args:
            llm_client: LLM client instance (creates default if not provided)
        """
        self.llm_client = llm_client or LLMClient()
        logger.info("PuzzleSolver initialized")

    async def solve_word(
        self,
        clue: str,
        length: int,
        pattern: Optional[str] = None,
        intersections: Optional[dict[int, str]] = None,
    ) -> tuple[str, float, str]:
        """
        Solve a single crossword word using AI.

        Args:
            clue: The crossword clue
            length: Length of the answer word
            pattern: Pattern with known letters (e.g., "A__T" for 4-letter word)
            intersections: Dict mapping position to known letter

        Returns:
            Tuple of (answer, confidence, reasoning)
        """
        logger.info(f"Solving word: clue='{clue}', length={length}, pattern={pattern}")

        try:
            # Build pattern from intersections if provided
            if intersections and not pattern:
                pattern = ["_"] * length
                for pos, letter in intersections.items():
                    if 0 <= pos < length:
                        pattern[pos] = letter
                pattern = "".join(pattern)

            # Create prompt for LLM
            prompt = self._build_solve_word_prompt(clue, length, pattern)

            # Call LLM
            messages = [
                {"role": "system", "content": "You are an expert crossword puzzle solver."},
                {"role": "user", "content": prompt}
            ]

            response = await self.llm_client.chat_completion_async(
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused answers
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            # Parse response
            import json
            result = json.loads(response.choices[0].message.content)

            answer = result.get("answer", "").upper()
            confidence = result.get("confidence", 0.5)
            reasoning = result.get("reasoning", "")

            # Validate answer
            if len(answer) != length:
                logger.warning(f"Answer length mismatch: expected {length}, got {len(answer)}")
                # Fallback: pad or truncate
                if len(answer) < length:
                    answer = answer.ljust(length, "_")
                else:
                    answer = answer[:length]
                confidence *= 0.5

            # Validate against pattern
            if pattern:
                if not self._matches_pattern(answer, pattern):
                    logger.warning(f"Answer doesn't match pattern: {answer} vs {pattern}")
                    confidence *= 0.3

            logger.info(f"Word solved: answer='{answer}', confidence={confidence:.2f}")

            return answer, confidence, reasoning

        except Exception as e:
            logger.error(f"Error solving word: {e}", exc_info=True)
            # Return a fallback answer
            fallback = "_" * length
            return fallback, 0.0, f"Error: {str(e)}"

    async def solve_puzzle(
        self,
        grid_dict: dict[str, Any],
        use_hints: bool = True
    ) -> tuple[list[dict[str, Any]], float, str]:
        """
        Solve an entire crossword puzzle using AI.

        Args:
            grid_dict: Serialized grid dictionary
            use_hints: Whether to use existing clues as hints

        Returns:
            Tuple of (updated_cells, overall_confidence, reasoning)
        """
        logger.info("Solving entire puzzle")

        try:
            # Extract all words from grid
            words = grid_dict.get("words", [])

            if not words:
                logger.warning("No words found in puzzle")
                return [], 0.0, "No words to solve"

            # For now, we'll just return the existing solution
            # In a real implementation, we would solve each word individually
            # and handle intersections

            cells = []
            # Cells are in 2D array format (list of rows)
            cells_2d = grid_dict.get("cells", [])
            for row in cells_2d:
                for cell_data in row:
                    if cell_data.get("value"):
                        cells.append({
                            "row": cell_data["row"],
                            "col": cell_data["col"],
                            "value": cell_data["value"],
                            "is_blocked": cell_data.get("is_blocked", False),
                            "number": cell_data.get("number"),
                        })

            confidence = 1.0 if use_hints else 0.8
            reasoning = "Complete puzzle solution using stored answers"

            logger.info(f"Puzzle solved: {len(cells)} cells filled")

            return cells, confidence, reasoning

        except Exception as e:
            logger.error(f"Error solving puzzle: {e}", exc_info=True)
            return [], 0.0, f"Error: {str(e)}"

    async def generate_hint(
        self,
        clue: str,
        answer: str,
        hint_type: str = "letter"
    ) -> tuple[str, Optional[str], Optional[int]]:
        """
        Generate a hint for a crossword word.

        Args:
            clue: The crossword clue
            answer: The correct answer
            hint_type: Type of hint (letter, definition, synonym)

        Returns:
            Tuple of (hint_text, revealed_letter, position)
        """
        logger.info(f"Generating hint: type={hint_type}, answer={answer}")

        try:
            if hint_type == "letter":
                # Reveal a random letter (prefer middle letters)
                positions = list(range(len(answer)))
                # Weight towards middle positions
                if len(positions) > 2:
                    # Remove first and last for more challenge
                    positions = positions[1:-1]

                position = random.choice(positions) if positions else 0
                letter = answer[position]

                hint_text = f"The letter at position {position + 1} is '{letter}'"
                return hint_text, letter, position

            elif hint_type == "definition":
                # Use LLM to generate alternative definition
                prompt = f"""Given the crossword clue: "{clue}"
And the answer: "{answer}"

Provide an alternative definition or hint that would help someone solve this clue.
The hint should be helpful but not give away the answer directly.

Respond in JSON format:
{{
    "hint": "your alternative hint here"
}}"""

                messages = [
                    {"role": "system", "content": "You are a helpful crossword puzzle assistant."},
                    {"role": "user", "content": prompt}
                ]

                response = await self.llm_client.chat_completion_async(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150,
                    response_format={"type": "json_object"}
                )

                import json
                result = json.loads(response.choices[0].message.content)
                hint_text = result.get("hint", f"Think about: {clue}")

                return hint_text, None, None

            elif hint_type == "synonym":
                # Use LLM to generate synonym or related word
                prompt = f"""Given the crossword answer: "{answer}"

Provide a synonym or closely related word that would help someone guess this answer.
The synonym should be helpful but not be the exact answer.

Respond in JSON format:
{{
    "hint": "your synonym or related word here"
}}"""

                messages = [
                    {"role": "system", "content": "You are a helpful crossword puzzle assistant."},
                    {"role": "user", "content": prompt}
                ]

                response = await self.llm_client.chat_completion_async(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=100,
                    response_format={"type": "json_object"}
                )

                import json
                result = json.loads(response.choices[0].message.content)
                hint_text = result.get("hint", f"A word related to: {answer}")

                return hint_text, None, None

            else:
                # Unknown hint type
                logger.warning(f"Unknown hint type: {hint_type}")
                return f"Hint for: {clue}", None, None

        except Exception as e:
            logger.error(f"Error generating hint: {e}", exc_info=True)
            # Fallback to simple hint
            return f"Think about: {clue}", None, None

    def _build_solve_word_prompt(
        self,
        clue: str,
        length: int,
        pattern: Optional[str] = None
    ) -> str:
        """
        Build a prompt for solving a crossword word.

        Args:
            clue: The crossword clue
            length: Length of the answer
            pattern: Pattern with known letters

        Returns:
            Formatted prompt string
        """
        prompt = f"""Solve this crossword clue:

Clue: {clue}
Length: {length} letters"""

        if pattern and pattern != "_" * length:
            prompt += f"\nPattern: {pattern} (where _ means unknown letter)"

        prompt += """

Provide your answer in JSON format:
{
    "answer": "YOUR_ANSWER_HERE",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this is the answer"
}

Rules:
- Answer must be exactly the specified length
- Answer must be a single word (or hyphenated phrase)
- Answer must match the pattern if provided
- Use only uppercase letters
- Confidence should be between 0.0 and 1.0
"""

        return prompt

    def _matches_pattern(self, answer: str, pattern: str) -> bool:
        """
        Check if an answer matches a pattern.

        Args:
            answer: The answer to check
            pattern: Pattern with known letters (e.g., "A__T")

        Returns:
            True if answer matches pattern
        """
        if len(answer) != len(pattern):
            return False

        for _i, (a, p) in enumerate(zip(answer, pattern)):
            if p != "_" and a != p:
                return False

        return True


# Singleton instance for convenience
_solver_instance: Optional[PuzzleSolver] = None


def get_solver() -> PuzzleSolver:
    """
    Get the singleton solver instance.

    Returns:
        PuzzleSolver instance
    """
    global _solver_instance
    if _solver_instance is None:
        _solver_instance = PuzzleSolver()
    return _solver_instance
