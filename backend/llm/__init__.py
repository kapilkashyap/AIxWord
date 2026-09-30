"""
LLM integration for crossword puzzle generation.

This package provides OpenAI client wrapper and prompt templates for
interacting with language models.
"""

from .client import LLMClient, get_llm_client
from .prompts import PromptTemplates, prompts

__all__ = [
    # Client
    "LLMClient",
    "get_llm_client",
    # Prompts
    "PromptTemplates",
    "prompts",
]
