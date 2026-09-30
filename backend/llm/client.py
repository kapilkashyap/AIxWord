"""
OpenAI client wrapper for LLM interactions.

This module provides a clean interface for interacting with OpenAI's API,
with support for structured outputs, error handling, and retry logic.
"""

import json
import logging
from typing import Any, Optional

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Wrapper for OpenAI API client with convenience methods.

    This class provides:
    - Synchronous and asynchronous API calls
    - Structured output parsing
    - Error handling and logging
    - Configuration management
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            api_key: OpenAI API key (uses config if not provided)
            model: Model name (uses config if not provided)
        """
        settings = get_settings()

        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.temperature = settings.openai_temperature

        # Initialize clients
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

        logger.info(f"LLM client initialized with model: {self.model}")

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[dict[str, str]] = None,
    ) -> ChatCompletion:
        """
        Create a chat completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (uses default if not provided)
            max_tokens: Maximum tokens in response
            response_format: Response format specification (e.g., {"type": "json_object"})

        Returns:
            ChatCompletion response from OpenAI

        Raises:
            Exception: If API call fails
        """
        temp = temperature if temperature is not None else self.temperature

        logger.debug(
            f"Creating chat completion: model={self.model}, "
            f"temperature={temp}, messages={len(messages)}"
        )

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
            }

            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            if response_format is not None:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)

            logger.debug(
                f"Chat completion successful: "
                f"tokens={response.usage.total_tokens if response.usage else 'unknown'}"
            )

            return response

        except Exception as e:
            logger.error(f"Chat completion failed: {e}", exc_info=True)
            raise

    async def chat_completion_async(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[dict[str, str]] = None,
    ) -> ChatCompletion:
        """
        Create a chat completion asynchronously.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (uses default if not provided)
            max_tokens: Maximum tokens in response
            response_format: Response format specification (e.g., {"type": "json_object"})

        Returns:
            ChatCompletion response from OpenAI

        Raises:
            Exception: If API call fails
        """
        temp = temperature if temperature is not None else self.temperature

        logger.debug(
            f"Creating async chat completion: model={self.model}, "
            f"temperature={temp}, messages={len(messages)}"
        )

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
            }

            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            if response_format is not None:
                kwargs["response_format"] = response_format

            response = await self.async_client.chat.completions.create(**kwargs)

            logger.debug(
                f"Async chat completion successful: "
                f"tokens={response.usage.total_tokens if response.usage else 'unknown'}"
            )

            return response

        except Exception as e:
            logger.error(f"Async chat completion failed: {e}", exc_info=True)
            raise

    def get_text_response(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Get text response from chat completion.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Text content from the response
        """
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content
        if content is None:
            logger.warning("Response content is None")
            return ""

        return content

    async def get_text_response_async(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Get text response from chat completion asynchronously.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Text content from the response
        """
        response = await self.chat_completion_async(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content
        if content is None:
            logger.warning("Async response content is None")
            return ""

        return content

    def get_json_response(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Get JSON response from chat completion.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Parsed JSON response as dictionary

        Raises:
            json.JSONDecodeError: If response is not valid JSON
        """
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if content is None:
            logger.warning("JSON response content is None")
            return {}

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {content}")
            raise

    async def get_json_response_async(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Get JSON response from chat completion asynchronously.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Parsed JSON response as dictionary

        Raises:
            json.JSONDecodeError: If response is not valid JSON
        """
        response = await self.chat_completion_async(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if content is None:
            logger.warning("Async JSON response content is None")
            return {}

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse async JSON response: {e}")
            logger.debug(f"Response content: {content}")
            raise

    def get_structured_response(
        self,
        messages: list[dict[str, str]],
        response_model: type[BaseModel],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> BaseModel:
        """
        Get structured response parsed into a Pydantic model.

        Args:
            messages: List of message dictionaries
            response_model: Pydantic model class to parse response into
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Instance of response_model with parsed data

        Raises:
            ValidationError: If response doesn't match model schema
        """
        json_response = self.get_json_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response_model(**json_response)

    async def get_structured_response_async(
        self,
        messages: list[dict[str, str]],
        response_model: type[BaseModel],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> BaseModel:
        """
        Get structured response parsed into a Pydantic model asynchronously.

        Args:
            messages: List of message dictionaries
            response_model: Pydantic model class to parse response into
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Instance of response_model with parsed data

        Raises:
            ValidationError: If response doesn't match model schema
        """
        json_response = await self.get_json_response_async(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response_model(**json_response)


# Singleton instance for convenience
_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get the singleton LLM client instance.

    Returns:
        LLMClient instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = LLMClient()
    return _client_instance
