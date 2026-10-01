# AIxWord Backend Architecture - Deep Dive

**Document Version:** 1.0  
**Last Updated:** 2026-09-29  
**Author:** Technical Documentation Team  
**Purpose:** Interview preparation and technical reference

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Multi-Agent Architecture](#multi-agent-architecture)
3. [LangGraph Workflow Orchestration](#langgraph-workflow-orchestration)
4. [State Management](#state-management)
5. [Domain-Driven Design](#domain-driven-design)
6. [AI/LLM Integration](#aillm-integration)
7. [API Layer](#api-layer)
8. [Design Patterns & Principles](#design-patterns--principles)

---

## Executive Summary

AIxWord is a **multi-agent AI system** that generates crossword puzzles using **LangGraph** for workflow orchestration and **OpenAI's GPT models** for intelligent word generation and placement. The system demonstrates advanced AI engineering concepts including:

- **Multi-agent collaboration** (PlannerAgent + WordGeneratorAgent)
- **State machine orchestration** via LangGraph
- **Prompt engineering** for structured LLM outputs
- **Domain-driven design** with clean separation of concerns
- **Iterative refinement** with validation and retry logic

### Key Technical Achievements

✅ **Multi-Agent System**: Two specialized agents collaborate through shared state  
✅ **LangGraph Integration**: State machine manages complex workflow transitions  
✅ **Prompt Engineering**: Structured JSON outputs from LLMs with validation  
✅ **Domain Logic**: Grid engine with collision detection and intersection validation  
✅ **Scalable Architecture**: Clean separation enables future enhancements (RAG, caching, persistence)

---

## Multi-Agent Architecture

### Overview

The system uses a **two-agent collaborative architecture** where each agent has a specialized role:

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│                                                              │
│  ┌──────────────┐         ┌──────────────────────┐         │
│  │              │         │                      │         │
│  │   Planner    │────────▶│  WordGenerator       │         │
│  │   Agent      │         │  Agent               │         │
│  │              │         │                      │         │
│  └──────────────┘         └──────────────────────┘         │
│         │                           │                       │
│         │                           │                       │
│         ▼                           ▼                       │
│  ┌─────────────────────────────────────────────┐           │
│  │          Shared Agent State                 │           │
│  │  (Grid, Words, Placements, Metadata)        │           │
│  └─────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Agent 1: PlannerAgent

**File:** `backend/agents/planner.py`

**Responsibilities:**
1. **Strategic Planning**: Analyzes current grid state and creates placement strategy
2. **Word Candidate Generation**: Uses LLM to generate thematically relevant words
3. **Placement Prioritization**: Decides which words to place and where
4. **Termination Logic**: Determines when puzzle generation should stop

**Key Methods:**
- `analyze_grid_state()`: Extracts grid metrics (fill rate, intersections, available spaces)
- `generate_placement_plan()`: Calls LLM to create strategic plan
- `_should_stop_planning()`: Evaluates stopping conditions

**LLM Interaction:**
```python
# Planner calls OpenAI with structured prompt
response = llm_client.get_json_response(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.7  # Balanced creativity
)

# Expected JSON structure:
{
    "action": "ADD_WORD",
    "reasoning": "Strategy explanation",
    "word_candidates": [
        {"word": "OCEAN", "clue": "Large body of water", "priority": 0.9}
    ],
    "placement_plan": [
        {
            "word": "OCEAN",
            "start_row": 0,
            "start_col": 0,
            "direction": "across",
            "priority": 0.9
        }
    ]
}
```

**Decision Logic:**
- **Continue**: If min_words not reached and iterations remaining
- **Stop**: If requirements met OR max iterations reached OR grid >90% full

### Agent 2: WordGeneratorAgent

**File:** `backend/agents/word_generator.py`

**Responsibilities:**
1. **Pattern Extraction**: Identifies letter constraints from existing grid
2. **Word Generation**: Uses LLM to generate words matching specific patterns
3. **Placement Execution**: Places words on grid with validation
4. **Failure Tracking**: Records failed placements for retry logic

**Key Methods:**
- `extract_pattern()`: Builds pattern like "A__LE" from grid state
- `get_intersecting_constraints()`: Identifies required letters from crossing words
- `generate_word()`: Calls LLM to generate word matching pattern
- `execute_placement()`: Validates and places word on grid

**Pattern Matching Example:**
```python
# Grid has "OCEAN" across at row 0
# Planning to place word DOWN at column 2 (intersects at 'E')

pattern = extract_pattern(grid, placement_plan)
# Returns: Pattern("_E___") for 5-letter word with 'E' at position 1

constraints = get_intersecting_constraints(grid, placement_plan)
# Returns: [{"position": 1, "letter": "E", "intersecting_word": "OCEAN"}]

# LLM generates: "BEACH" (matches pattern _E___)
```

**Validation Pipeline:**
1. **Pattern Match**: Word must match extracted pattern exactly
2. **Grid Bounds**: Word must fit within grid dimensions
3. **Intersection Check**: Crossing letters must match
4. **Conflict Detection**: No letter mismatches with existing words

---

## LangGraph Workflow Orchestration

### Why LangGraph?

**LangGraph** is a framework for building stateful, multi-agent workflows with LLMs. We chose it because:

1. **State Management**: Built-in state passing between nodes
2. **Conditional Routing**: Dynamic workflow paths based on state
3. **Iteration Control**: Native support for loops and recursion limits
4. **Observability**: Clear workflow visualization and debugging
5. **LangChain Integration**: Seamless integration with LangChain ecosystem

### Workflow Graph Structure

**File:** `backend/agents/workflow.py`

```python
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("initialize", _initialize_node)
workflow.add_node("planner", _planner_node)
workflow.add_node("executor", _executor_node)

# Edges
workflow.set_entry_point("initialize")
workflow.add_edge("initialize", "planner")
workflow.add_edge("planner", "executor")

# Conditional routing
workflow.add_conditional_edges(
    "executor",
    _should_continue,
    {
        "continue": "planner",  # Loop back for next iteration
        "end": END              # Terminate workflow
    }
)
```

### Workflow Execution Flow

```
┌─────────────┐
│ START       │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Initialize Node     │  Creates empty grid, sets initial state
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Planner Node        │  Analyzes grid, generates placement plan
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Executor Node       │  Executes placements, updates grid
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Should Continue?    │  Check requirements & iteration limit
└──────┬──────────────┘
       │
       ├─── continue ───┐
       │                │
       ▼                │
     ┌─────┐            │
     │ END │◀───────────┘
     └─────┘
```

### Node Implementations

#### 1. Initialize Node
```python
def _initialize_node(state: AgentState) -> dict[str, Any]:
    """
    Creates empty grid and sets initial state.
    
    Returns:
        - grid_state: Empty NxN grid
        - status: "planning"
        - iteration: 0
    """
    grid = CrosswordGrid(size=state.requirements.grid_size)
    return {
        "grid_state": grid.to_dict(),
        "status": "planning",
        "iteration": 0
    }
```

#### 2. Planner Node
```python
def _planner_node(state: AgentState) -> dict[str, Any]:
    """
    Generates strategic placement plan using PlannerAgent.
    
    Process:
    1. Analyze current grid state
    2. Call LLM to generate word candidates
    3. Create placement plan
    4. Validate grid bounds
    5. Update state with candidates
    
    Returns:
        - placement_plan: List of PlacementPlan objects
        - word_candidates: List of WordCandidate objects
        - status: "planning" or "completed" (if stopped)
    """
    action = planner_agent.generate_placement_plan(state)
    
    if action.action == "STOP":
        return {"status": "completed", "stop_reason": action.stop_reason}
    
    # Validate placements fit within grid bounds
    valid_placements = []
    for plan in action.placement_plan:
        if validate_grid_bounds(plan, state.requirements.grid_size):
            valid_placements.append(plan)
        else:
            state.add_failed_placement(plan.word, "Grid bounds exceeded")
    
    return {
        "placement_plan": valid_placements,
        "word_candidates": action.word_candidates
    }
```

#### 3. Executor Node
```python
def _executor_node(state: AgentState) -> dict[str, Any]:
    """
    Executes placement plan using WordGeneratorAgent.
    
    Process:
    1. For each placement in plan:
       a. Extract pattern from grid
       b. Generate word matching pattern
       c. Validate placement
       d. Place word on grid
    2. Increment iteration counter
    3. Update grid state
    
    Returns:
        - grid_state: Updated grid with new words
        - iteration: Incremented counter
        - status: "executing", "completed", or "failed"
    """
    successful = word_generator_agent.execute_placement_plan(
        state, 
        max_placements=5  # Limit per iteration
    )
    
    new_iteration = state.iteration + 1
    
    # Determine status
    if state.is_requirements_met():
        status = "completed"
    elif new_iteration >= state.max_iterations:
        status = "failed"
    else:
        status = "executing"
    
    return {
        "iteration": new_iteration,
        "grid_state": state.get_grid().to_dict(),
        "status": status
    }
```

#### 4. Should Continue Decision
```python
def _should_continue(state: AgentState) -> Literal["continue", "end"]:
    """
    Determines if workflow should continue or terminate.
    
    Continue if:
    - Requirements not met (min_words not reached)
    - Iterations remaining (iteration < max_iterations)
    - No fatal errors
    
    End if:
    - status == "completed" (requirements met)
    - status == "failed" (max iterations or error)
    """
    if state.status in ["completed", "failed"]:
        return "end"
    
    if state.iteration >= state.max_iterations:
        return "end"
    
    if not state.is_requirements_met():
        return "continue"
    
    return "end"
```

### Recursion Limit Management

**Critical Configuration:**

```python
# Dynamic recursion limit based on max_iterations
recursion_limit = max(100, int(max_iterations * 4 * 1.2))

# Each iteration involves ~4 graph node executions:
# 1. planner node
# 2. executor node
# 3. should_continue check
# 4. (loop back to planner)

# Example: max_iterations=50 → recursion_limit=240
```

**Why Dynamic?**
- LangGraph counts every node execution toward recursion limit
- Fixed limit (25 default) causes failures with high iteration counts
- Dynamic calculation ensures limit scales with user configuration

---

## State Management

### AgentState Schema

**File:** `backend/agents/state.py`

The `AgentState` is a **Pydantic model** that serves as the shared memory between agents:

```python
class AgentState(BaseModel):
    # Input requirements
    requirements: PuzzleRequirements
    
    # Grid state (serialized for LangGraph compatibility)
    grid_state: Optional[dict[str, Any]] = None
    
    # Planning data
    word_candidates: list[WordCandidate] = []
    placement_plan: list[PlacementPlan] = []
    
    # Execution tracking
    placed_words: list[str] = []
    failed_placements: list[dict[str, Any]] = []
    
    # Iteration control
    iteration: int = 0
    max_iterations: int = 50
    
    # Status
    status: Literal["initializing", "planning", "executing", "completed", "failed"]
    error_message: Optional[str] = None
    
    # Metadata
    metadata: dict[str, Any] = {}
```

### State Transitions

```
initializing → planning → executing → planning → ... → completed
                                                      ↘ failed
```

### Key State Methods

```python
# Grid serialization (LangGraph requires JSON-serializable state)
def get_grid() -> Optional[CrosswordGrid]:
    """Deserialize grid from dict."""
    return CrosswordGrid.from_dict(self.grid_state)

def set_grid(grid: CrosswordGrid) -> None:
    """Serialize grid to dict."""
    self.grid_state = grid.to_dict()

# Tracking
def add_placed_word(word: str) -> None:
    """Track successfully placed word."""
    self.placed_words.append(word)

def add_failed_placement(word: str, reason: str, details: dict) -> None:
    """Track failed placement for debugging."""
    self.failed_placements.append({
        "word": word,
        "reason": reason,
        "details": details,
        "iteration": self.iteration
    })

# Validation
def is_requirements_met() -> bool:
    """Check if minimum word count reached."""
    return len(self.placed_words) >= self.requirements.min_words

def is_max_iterations_reached() -> bool:
    """Check if iteration limit hit."""
    return self.iteration >= self.max_iterations
```

---

## Domain-Driven Design

### Domain Model Hierarchy

```
CrosswordGrid (Aggregate Root)
├── Cell[][] (Value Objects)
├── Word[] (Entities)
│   ├── WordPlacement (Value Object)
│   └── Direction (Enum)
├── Pattern (Value Object)
└── WordValidator (Domain Service)
```

### Core Domain Classes

#### CrosswordGrid
**File:** `backend/domain/grid.py`

**Responsibilities:**
- Manage 2D grid of cells
- Place and remove words
- Detect collisions and intersections
- Calculate fill rate and statistics

**Key Operations:**
```python
# Word placement with validation
def place_word(placement: WordPlacement) -> bool:
    """
    Place word on grid with full validation.
    
    Checks:
    - Grid bounds
    - Letter conflicts
    - Intersection validity
    - Blocked cells
    """
    if not self.can_place_word(placement):
        return False
    
    # Place letters
    for i, (row, col) in enumerate(placement.get_cells()):
        self.set_cell(row, col, placement.word[i])
    
    # Create Word entity
    word = Word(
        text=placement.word,
        clue=placement.clue,
        start_row=placement.start_row,
        start_col=placement.start_col,
        direction=placement.direction
    )
    self.words.append(word)
    return True

# Intersection detection
def get_word_at(row: int, col: int, direction: Direction) -> Optional[Word]:
    """Find word at position in given direction."""
    for word in self.words:
        if word.contains_position(row, col) and word.direction == direction:
            return word
    return None
```

#### WordValidator
**File:** `backend/domain/validator.py`

**Responsibilities:**
- Validate word placements
- Check grid bounds
- Detect conflicts
- Extract patterns

**Validation Pipeline:**
```python
def validate_placement(grid: CrosswordGrid, placement: WordPlacement) -> ValidationResult:
    """
    Comprehensive validation with detailed error reporting.
    
    Checks (in order):
    1. Bounds: Word fits in grid
    2. Format: Valid word and clue
    3. Conflicts: No letter mismatches
    4. Intersections: Valid crossings
    """
    result = ValidationResult(is_valid=True)
    
    # 1. Bounds check
    if not _validate_bounds(grid, placement, result):
        return result  # Early exit on bounds failure
    
    # 2. Format check
    if not _validate_format(placement, result):
        return result
    
    # 3. Conflict check
    if not _validate_conflicts(grid, placement, result):
        return result
    
    # 4. Intersection check
    _validate_intersections(grid, placement, result)
    
    return result
```

#### Pattern
**File:** `backend/domain/pattern.py`

**Responsibilities:**
- Represent word patterns (e.g., "A__LE")
- Match words against patterns
- Extract patterns from grid

**Pattern Matching:**
```python
class Pattern:
    def __init__(self, pattern: str):
        """
        Create pattern from string.
        
        Examples:
        - "OCEAN" → fully known pattern
        - "_____" → 5-letter unknown pattern
        - "A__LE" → partial pattern (A at 0, LE at 3-4)
        """
        self.pattern = pattern.upper()
        self.length = len(pattern)
        self.known_positions = {
            i: char for i, char in enumerate(pattern) if char != "_"
        }
    
    def matches(self, word: str) -> bool:
        """Check if word matches this pattern."""
        if len(word) != self.length:
            return False
        
        for pos, required_char in self.known_positions.items():
            if word[pos] != required_char:
                return False
        
        return True
```

---

## AI/LLM Integration

### OpenAI Client Architecture

**File:** `backend/llm/client.py`

**Design Principles:**
1. **Abstraction**: Hide OpenAI SDK details behind clean interface
2. **Error Handling**: Comprehensive error catching and logging
3. **Flexibility**: Support both sync and async operations
4. **Configuration**: Centralized model and temperature settings

**Client Interface:**
```python
class LLMClient:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    def get_json_response(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> dict[str, Any]:
        """
        Get structured JSON response from LLM.
        
        Process:
        1. Call OpenAI with response_format={"type": "json_object"}
        2. Parse JSON from response
        3. Validate structure
        4. Return parsed dict
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
```

### Prompt Engineering Strategy

#### Structured Prompts

**System Prompt** (defines role and capabilities):
```python
"""You are an expert crossword puzzle planner with deep knowledge of 
puzzle construction principles. Your role is to create strategic plans 
for placing words on a crossword grid.

**Response Format:**
You must respond in JSON format with this exact structure:
{
    "action": "ADD_WORD",
    "reasoning": "...",
    "word_candidates": [...],
    "placement_plan": [...]
}
"""
```

**User Prompt** (provides context and task):
```python
f"""Generate a strategic crossword puzzle plan for the topic: "{topic}"

**Puzzle Requirements:**
- Grid size: {grid_size}x{grid_size}
- Minimum words needed: {min_words}
- Difficulty level: {difficulty}

**Current Grid State:**
- Words placed: {word_count}
- Fill rate: {fill_rate:.1%}

**Your Task:**
Generate 3-8 word candidates with placement plans...
"""
```

#### Temperature Tuning

**Planner Agent**: `temperature=0.7`
- Balanced creativity and consistency
- Strategic planning benefits from some randomness
- Avoids repetitive patterns

**Word Generator Agent**: `temperature=0.8`
- Higher creativity for word generation
- More diverse vocabulary
- Better for finding words matching constraints

#### JSON Schema Enforcement

**Technique**: Use `response_format={"type": "json_object"}` + Pydantic validation

```python
# 1. Request JSON from OpenAI
response = llm_client.get_json_response(
    messages=messages,
    response_format={"type": "json_object"}
)

# 2. Validate with Pydantic
action = PlannerAction(**response)  # Raises ValidationError if invalid

# 3. Handle validation errors
try:
    action = PlannerAction(**response)
except ValidationError as e:
    logger.error(f"Invalid LLM response: {e}")
    # Fallback or retry logic
```

### Model Selection Rationale

**Current:** `gpt-4o-mini`

**Why?**
- **Cost**: $0.15/1M input tokens (94% cheaper than gpt-4o)
- **Speed**: Fastest inference time
- **Quality**: Sufficient for crossword word generation
- **POC-Appropriate**: Excellent for proof-of-concept

**Comparison:**

| Model | Input Cost | Output Cost | Use Case |
|-------|-----------|-------------|----------|
| gpt-4o | $2.50/1M | $10.00/1M | Production, complex reasoning |
| gpt-4o-mini | $0.15/1M | $0.60/1M | POC, testing, simple tasks |
| gpt-3.5-turbo | $0.50/1M | $1.50/1M | Legacy, not recommended |

**When to Upgrade:**
- Production deployment with paying users
- Larger grids (15×15, 21×21)
- More complex clue generation (cryptic crosswords)
- Higher quality requirements

---

## API Layer

### FastAPI Architecture

**File:** `backend/main.py`, `backend/api/routes/puzzles.py`

**Design:**
- **RESTful**: Standard HTTP methods and status codes
- **Async**: Non-blocking I/O for scalability
- **Validation**: Pydantic models for request/response
- **Documentation**: Auto-generated OpenAPI docs

**Key Endpoints:**

```python
# Generate puzzle
POST /api/puzzles/generate
Request: {
    "topic": "Ocean",
    "grid_size": 8,
    "difficulty": "medium",
    "max_iterations": 50
}
Response: {
    "success": true,
    "puzzle_id": "uuid",
    "grid": {...},
    "clues": {...}
}

# Solve word
POST /api/puzzles/{puzzle_id}/solve-word
Request: {
    "clue_number": 1,
    "direction": "across"
}
Response: {
    "success": true,
    "word": "OCEAN",
    "cells": [...]
}

# Get hint
POST /api/puzzles/{puzzle_id}/hint
Request: {
    "clue_number": 1,
    "direction": "across",
    "hint_type": "definition"
}
Response: {
    "success": true,
    "hint": "Think of a large body of saltwater..."
}
```

### Orchestrator Pattern

**File:** `backend/agents/orchestrator.py`

**Purpose**: High-level facade over workflow complexity

```python
class PuzzleOrchestrator:
    """
    Simplifies workflow interaction for API layer.
    
    Responsibilities:
    - Request validation
    - Workflow execution
    - Result transformation
    - Error handling
    - Retry logic
    """
    
    def generate_puzzle(self, request: PuzzleGenerationRequest) -> PuzzleGenerationResult:
        """
        Generate puzzle with automatic error handling.
        
        Process:
        1. Validate request
        2. Execute LangGraph workflow
        3. Transform state to result
        4. Handle errors gracefully
        """
        # Validate
        is_valid, error = self.validate_request(request)
        if not is_valid:
            return PuzzleGenerationResult(success=False, error_message=error)
        
        # Execute workflow
        final_state = self.workflow.generate_puzzle(
            topic=request.topic,
            grid_size=request.grid_size,
            max_iterations=request.max_iterations
        )
        
        # Transform result
        return self._state_to_result(final_state)
```

---

## Design Patterns & Principles

### 1. **Agent Pattern**
- **What**: Autonomous entities with specialized responsibilities
- **Why**: Separation of concerns, testability, scalability
- **Where**: PlannerAgent, WordGeneratorAgent

### 2. **State Machine Pattern**
- **What**: Explicit state transitions with validation
- **Why**: Predictable workflow, easy debugging, clear logic
- **Where**: LangGraph workflow nodes and edges

### 3. **Repository Pattern** (Implicit)
- **What**: Abstraction over data access
- **Why**: Decouples domain from persistence
- **Where**: In-memory storage (future: database repository)

### 4. **Strategy Pattern**
- **What**: Interchangeable algorithms
- **Why**: Flexibility in word generation strategies
- **Where**: Different hint types, difficulty levels

### 5. **Facade Pattern**
- **What**: Simplified interface over complex subsystem
- **Why**: Easy API integration, hides complexity
- **Where**: PuzzleOrchestrator

### 6. **Domain-Driven Design**
- **What**: Business logic in domain models
- **Why**: Rich domain model, clear boundaries
- **Where**: Grid, Word, Pattern, Validator

### SOLID Principles

✅ **Single Responsibility**: Each agent has one clear purpose  
✅ **Open/Closed**: Extensible (add new agents) without modifying existing  
✅ **Liskov Substitution**: Agents implement common interface  
✅ **Interface Segregation**: Minimal, focused interfaces  
✅ **Dependency Inversion**: Depend on abstractions (LLMClient interface)

---

## Summary

This architecture demonstrates:

1. **Advanced AI Engineering**: Multi-agent collaboration with LLMs
2. **Production-Ready Patterns**: Clean architecture, error handling, validation
3. **Scalability**: Designed for future enhancements (RAG, caching, persistence)
4. **Maintainability**: Clear separation of concerns, comprehensive logging
5. **Testability**: Isolated components, dependency injection

**Key Takeaway for Interviews:**

> "We built a multi-agent AI system using LangGraph to orchestrate two specialized agents—a strategic planner and a word generator—that collaborate through shared state to generate crossword puzzles. The system demonstrates advanced prompt engineering, state machine design, and domain-driven architecture, with a clean separation between AI logic, domain models, and API layers."

