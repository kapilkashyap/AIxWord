# Agents Module

This module contains the multi-agent system for crossword puzzle generation using LangGraph.

## Components

### State Management (`state.py`)
- **PuzzleRequirements**: Puzzle generation requirements
- **WordCandidate**: Candidate word for placement
- **PlacementPlan**: Strategic placement plan
- **AgentState**: Shared state across workflow

### Workflow Orchestration (`workflow.py`)
- **CrosswordWorkflow**: LangGraph StateGraph workflow
- **get_workflow()**: Singleton workflow instance

## Workflow Structure

```
initialize → planner → executor → should_continue
                ↑                      ↓
                └──────── continue ────┘
                              ↓
                            end
```

## Usage

```python
from agents import CrosswordWorkflow

workflow = CrosswordWorkflow()
final_state = workflow.generate_puzzle(
    topic="Science",
    grid_size=8,
    min_words=10,
    max_words=15,
    difficulty="medium",
)
```

## Next Steps

The workflow foundation is complete. Next phase will implement:
1. PlannerAgent - generates word candidates and placement strategy
2. WordGeneratorAgent - executes placement plan with LLM assistance
