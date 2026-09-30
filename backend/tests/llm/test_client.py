"""
Tests for LLM client wrapper.

This module tests the LLMClient class for OpenAI API interactions.
Note: These tests use mocking to avoid actual API calls.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice, CompletionUsage
from pydantic import BaseModel

from backend.llm.client import LLMClient, get_llm_client


class TestResponse(BaseModel):
    """Test response model for structured output tests."""

    word: str
    clue: str
    confidence: float


class TestLLMClient:
    """Tests for LLMClient class."""

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_client_initialization(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test LLM client initialization."""
        client = LLMClient(api_key="test-key", model="gpt-4")

        assert client.api_key == "test-key"
        assert client.model == "gpt-4"
        assert client.client is not None
        assert client.async_client is not None

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_client_default_config(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test client uses config defaults."""
        client = LLMClient()

        # Should use config values
        assert client.api_key is not None
        assert client.model is not None
        assert client.temperature is not None

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_singleton_pattern(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test singleton pattern for get_llm_client."""
        # Reset singleton
        import backend.llm.client as client_module
        client_module._client_instance = None

        client1 = get_llm_client()
        client2 = get_llm_client()

        assert client1 is client2

    def _create_mock_completion(self, content: str) -> ChatCompletion:
        """Helper to create mock ChatCompletion."""
        return ChatCompletion(
            id="test-id",
            choices=[
                Choice(
                    finish_reason="stop",
                    index=0,
                    message=ChatCompletionMessage(
                        content=content,
                        role="assistant",
                    ),
                )
            ],
            created=1234567890,
            model="gpt-4",
            object="chat.completion",
            usage=CompletionUsage(
                completion_tokens=10,
                prompt_tokens=20,
                total_tokens=30,
            ),
        )

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_chat_completion(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test chat completion."""
        # Setup mock
        mock_response = self._create_mock_completion("Test response")
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test message"}]

        response = client.chat_completion(messages)

        assert response.choices[0].message.content == "Test response"
        mock_openai.return_value.chat.completions.create.assert_called_once()

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_chat_completion_async(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test async chat completion."""
        # Setup mock
        mock_response = self._create_mock_completion("Async test response")
        mock_async_openai.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        client = LLMClient()
        messages = [{"role": "user", "content": "Test message"}]

        response = await client.chat_completion_async(messages)

        assert response.choices[0].message.content == "Async test response"

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_get_text_response(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test getting text response."""
        mock_response = self._create_mock_completion("Text response")
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        text = client.get_text_response(messages)

        assert text == "Text response"

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_get_text_response_async(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test getting text response asynchronously."""
        mock_response = self._create_mock_completion("Async text response")
        mock_async_openai.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        text = await client.get_text_response_async(messages)

        assert text == "Async text response"

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_get_json_response(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test getting JSON response."""
        json_content = '{"word": "SCIENCE", "clue": "Study", "confidence": 0.9}'
        mock_response = self._create_mock_completion(json_content)
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        json_data = client.get_json_response(messages)

        assert json_data["word"] == "SCIENCE"
        assert json_data["clue"] == "Study"
        assert json_data["confidence"] == 0.9

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_get_json_response_async(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test getting JSON response asynchronously."""
        json_content = '{"word": "HISTORY", "clue": "Past", "confidence": 0.85}'
        mock_response = self._create_mock_completion(json_content)
        mock_async_openai.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        json_data = await client.get_json_response_async(messages)

        assert json_data["word"] == "HISTORY"
        assert json_data["clue"] == "Past"
        assert json_data["confidence"] == 0.85

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_get_structured_response(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test getting structured response with Pydantic model."""
        json_content = '{"word": "PHYSICS", "clue": "Natural science", "confidence": 0.95}'
        mock_response = self._create_mock_completion(json_content)
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        response = client.get_structured_response(messages, TestResponse)

        assert isinstance(response, TestResponse)
        assert response.word == "PHYSICS"
        assert response.clue == "Natural science"
        assert response.confidence == 0.95

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_get_structured_response_async(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test getting structured response asynchronously."""
        json_content = '{"word": "BIOLOGY", "clue": "Life science", "confidence": 0.88}'
        mock_response = self._create_mock_completion(json_content)
        mock_async_openai.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        response = await client.get_structured_response_async(messages, TestResponse)

        assert isinstance(response, TestResponse)
        assert response.word == "BIOLOGY"
        assert response.clue == "Life science"
        assert response.confidence == 0.88

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_temperature_override(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test temperature parameter override."""
        mock_response = self._create_mock_completion("Test")
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        client.chat_completion(messages, temperature=0.5)

        # Verify temperature was passed
        call_kwargs = mock_openai.return_value.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.5

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_max_tokens_parameter(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test max_tokens parameter."""
        mock_response = self._create_mock_completion("Test")
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        client.chat_completion(messages, max_tokens=100)

        # Verify max_tokens was passed
        call_kwargs = mock_openai.return_value.chat.completions.create.call_args[1]
        assert call_kwargs["max_tokens"] == 100

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_response_format_parameter(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test response_format parameter for JSON mode."""
        mock_response = self._create_mock_completion('{"test": "data"}')
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        client.chat_completion(messages, response_format={"type": "json_object"})

        # Verify response_format was passed
        call_kwargs = mock_openai.return_value.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_none_content_handling(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test handling of None content in response."""
        # Create completion with None content
        completion = ChatCompletion(
            id="test-id",
            choices=[
                Choice(
                    finish_reason="stop",
                    index=0,
                    message=ChatCompletionMessage(
                        content=None,
                        role="assistant",
                    ),
                )
            ],
            created=1234567890,
            model="gpt-4",
            object="chat.completion",
        )

        mock_openai.return_value.chat.completions.create.return_value = completion

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        text = client.get_text_response(messages)
        assert text == ""

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_invalid_json_handling(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test handling of invalid JSON response."""
        mock_response = self._create_mock_completion("Not valid JSON")
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        with pytest.raises(Exception):  # Should raise JSONDecodeError
            client.get_json_response(messages)

    @patch("backend.llm.client.OpenAI")
    @patch("backend.llm.client.AsyncOpenAI")
    def test_api_error_handling(
        self, mock_async_openai: MagicMock, mock_openai: MagicMock
    ) -> None:
        """Test handling of API errors."""
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        client = LLMClient()
        messages = [{"role": "user", "content": "Test"}]

        with pytest.raises(Exception) as exc_info:
            client.chat_completion(messages)

        assert "API Error" in str(exc_info.value)
