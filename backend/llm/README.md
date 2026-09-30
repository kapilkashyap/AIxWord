# LLM Module

This module provides OpenAI integration for the crossword puzzle generation system.

## Components

### Client (`client.py`)
- **LLMClient**: OpenAI API wrapper
- **get_llm_client()**: Singleton client instance

### Prompts (`prompts.py`)
- **PromptTemplates**: Collection of prompt templates
- **prompts**: Singleton instance

## Features

### LLM Client
- Sync and async API calls
- Text, JSON, and structured responses
- Error handling and logging
- Configuration management

### Prompt Templates
- Planner prompts (word generation, strategy)
- Word generator prompts (pattern matching)
- Clue generator prompts (difficulty-aware)
- Solver prompts (puzzle solving)
- Hint generator prompts (progressive hints)

## Usage

```python
from llm import get_llm_client, prompts

client = get_llm_client()

# Get JSON response
messages = [
    {"role": "system", "content": prompts.planner_system_prompt()},
    {"role": "user", "content": prompts.planner_user_prompt(...)},
]
response = client.get_json_response(messages)
```
