# AIxWord Multi-Agent System Documentation

**Version:** 1.0.0  
**Last Updated:** September 28, 2026  
**Status:** Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agents](#agents)
4. [Workflow](#workflow)
5. [State Management](#state-management)
6. [LLM Integration](#llm-integration)
7. [Error Handling](#error-handling)
8. [Performance](#performance)
9. [Examples](#examples)
10. [Best Practices](#best-practices)

---

## Overview

The AIxWord multi-agent system is the core intelligence behind crossword puzzle generation. It uses **LangGraph** to orchestrate two specialized AI agents that work together to create coherent, topic-based crossword puzzles.

### Key Concepts

**Multi-Agent System**: A system where multiple autonomous agents collaborate to achieve a common goal. In AIxWord, agents specialize in different aspects of puzzle generation:
- **PlannerAgent**: Strategic planning and word selection
- **WordGeneratorAgent**: Word generation and grid placement

**LangGraph**: A framework for building stateful, multi-agent workflows using directed graphs. It provides:
- State management across agents
- Conditional routing between nodes
- Iterative execution patterns
- Error recovery mechanisms

### Why Multi-Agent?

**Separation of Concerns**: Each agent focuses on a specific task:
- Planning requires strategic thinking and topic knowledge
- Generation requires pattern matching and constraint satisfaction

**Iterative Refinement**: Agents work in a loop:
1. Planner analyzes current state and creates plan
2. Generator executes plan and updates grid
3. Planner evaluates results and adjusts strategy
4. Repeat until puzzle is complete

**Modularity**: Agents can be:
- Developed independently
- Tested in isolation
- Replaced or upgraded without affecting others
- Extended with new capabilities

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              PuzzleOrchestrator                             │
│  (High-level interface for puzzle generation)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ generate_puzzle_async()
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           LangGraph Workflow (StateGraph)                   │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │Initialize│ -> │ Planner  │ -> │ Executor │            │
│  │  Node    │    │  Agent   │    │  Agent   │            │
│  └──────────┘    └──────────┘    └────┬─────┘            │
│                        ▲                │                  │
│                        │                ▼                  │
│                        │         ┌──────────┐             │
│                        │         │ Should   │             │
│                        │         │Continue? │             │
│                        │         └────┬─────┘             │
│                        │              │                    │
│                        │      ┌───────┴────────┐          │
│                        │      │                │          │
│                        └──────┤ Continue       │ End      │
│                               │                │          │
│                               └────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                      │
                      │ LLM API Calls
                      ▼
            ┌─────────────────┐
            │   OpenAI API    │
            │   GPT-4 Turbo   │
            └─────────────────┘
```

### Component Hierarchy

```
PuzzleOrchestrator
├── CrosswordWorkflow (LangGraph StateGraph)
│   ├── Initialize Node
│   ├── Planner Node (PlannerAgent)
│   ├── Executor Node (WordGeneratorAgent)
│   └── Decision Node (should_continue)
├── PlannerAgent
│   ├── LLMClient
│   └── PlannerPrompts
└── WordGeneratorAgent
    ├── LLMClient
    ├── WordGeneratorPrompts
    └── WordValidator
```

### Data Flow

```
User Request
    ↓
PuzzleOrchestrator.generate_puzzle_async()
    ↓
CrosswordWorkflow.invoke()
    ↓
┌─────────────────────────────────────┐
│ LangGraph Execution Loop            │
│                                     │
│ 1. Initialize: Create empty grid   │
│    ↓                                │
│ 2. Planner: Generate word plan     │
│    ├─ Analyze grid state           │
│    ├─ Call LLM for word candidates │
│    └─ Create placement plan         │
│    ↓                                │
│ 3. Executor: Place words           │
│    ├─ Extract patterns from grid   │
│    ├─ Call LLM for word generation │
│    ├─ Validate placements          │
│    └─ Update grid                   │
│    ↓                                │
│ 4. Decision: Continue or end?      │
│    ├─ Check requirements met       │
│    ├─ Check max iterations         │
│    └─ Return to step 2 or end      │
│                                     │
└─────────────────────────────────────┘
    ↓
Return PuzzleGenerationResult
```

---

## Agents

### PlannerAgent

**Purpose**: Strategic planning for word placement

**Responsibilities**:
1. Analyze current grid state
2. Generate word candidates based on topic
3. Create strategic placement plan
4. Decide when to stop puzzle generation
5. Adapt strategy based on execution results

**Key Methods**:

```python
class PlannerAgent:
    def analyze_grid_state(state: AgentState) -> dict:
        """Analyze current grid and extract metrics"""
        
    def generate_word_candidates(state: AgentState) -> list[WordCandidate]:
        """Generate candidate words for the topic"""
        
    def create_placement_plan(state: AgentState) -> list[PlacementPlan]:
        """Create strategic placement plan"""
        
    def should_stop(state: AgentState) -> bool:
        """Decide if puzzle generation should stop"""
```

**LLM Interaction**:

The PlannerAgent uses GPT-4 to make strategic decisions:

```python
# System prompt
system_prompt = """
You are a strategic planner for crossword puzzle generation.
Your role is to analyze the current puzzle state and create
a strategic plan for placing words that:
1. Relate to the given topic
2. Fit well with existing words
3. Create interesting intersections
4. Maintain puzzle quality
"""

# User prompt
user_prompt = f"""
Topic: {topic}
Grid Size: {grid_size}x{grid_size}
Current State:
- Placed Words: {placed_words}
- Fill Rate: {fill_rate}
- Iteration: {iteration}

Requirements:
- Min Words: {min_words}
- Max Words: {max_words}
- Difficulty: {difficulty}

Task: Generate word candidates and create a placement plan.
"""
```

**Output Format**:

```json
{
  "action": "ADD_WORD",
  "reasoning": "Grid has good foundation, adding more words to increase density",
  "word_candidates": [
    {
      "word": "BIOLOGY",
      "clue": "Study of living organisms",
      "priority": 0.9,
      "category": "science"
    },
    ...
  ],
  "placement_plan": [
    {
      "word": "BIOLOGY",
      "clue": "Study of living organisms",
      "start_row": 0,
      "start_col": 0,
      "direction": "across",
      "priority": 0.9,
      "reasoning": "Good starting word, central to topic"
    },
    ...
  ]
}
```

### WordGeneratorAgent

**Purpose**: Execute placement plan by generating and placing words

**Responsibilities**:
1. Extract patterns from grid positions
2. Generate words that fit patterns using LLM
3. Validate word placements
4. Place words on grid
5. Handle placement failures and retries

**Key Methods**:

```python
class WordGeneratorAgent:
    def extract_pattern(grid: CrosswordGrid, plan: PlacementPlan) -> Pattern:
        """Extract current pattern from grid position"""
        
    def generate_word(pattern: Pattern, topic: str, clue: str) -> WordGenerationResult:
        """Generate word that fits pattern"""
        
    def validate_placement(grid: CrosswordGrid, placement: WordPlacement) -> bool:
        """Validate word can be placed"""
        
    def place_word(grid: CrosswordGrid, placement: WordPlacement) -> bool:
        """Place word on grid"""
```

**Pattern Extraction**:

The agent extracts patterns from the grid to constrain word generation:

```python
# Example: 5-letter word with 'A' at position 0 and 'E' at position 3
pattern = "A__LE"

# Pattern with no constraints
pattern = "_____"

# Pattern with multiple constraints
pattern = "B_O_O_Y"  # BIOLOGY
```

**LLM Interaction**:

```python
# System prompt
system_prompt = """
You are a word generator for crossword puzzles.
Generate words that:
1. Fit the given pattern (letters and blanks)
2. Relate to the topic
3. Match the clue
4. Are valid English words
5. Are appropriate for the difficulty level
"""

# User prompt
user_prompt = f"""
Topic: {topic}
Pattern: {pattern}  # e.g., "A__LE"
Direction: {direction}
Clue: {clue}
Difficulty: {difficulty}

Intersecting Words:
- Position 0: 'A' from "ATOM" (down)
- Position 3: 'L' from "CELL" (down)

Generate a word that fits this pattern.
"""
```

**Output Format**:

```json
{
  "word": "APPLE",
  "clue": "Common fruit, often red or green",
  "confidence": 0.85,
  "reasoning": "APPLE fits the pattern A__LE perfectly, intersects correctly with ATOM and CELL, and relates to the science topic (botany).",
  "alternatives": ["ANKLE", "ANGLE"]
}
```

---

## Workflow

### LangGraph StateGraph

The workflow is defined as a LangGraph StateGraph with four nodes:

```python
class CrosswordWorkflow:
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Add edges
        workflow.add_edge("initialize", "planner")
        workflow.add_edge("planner", "executor")
        
        # Add conditional edge
        workflow.add_conditional_edges(
            "executor",
            self._should_continue,
            {
                "continue": "planner",
                "end": END,
            }
        )
        
        return workflow.compile()
```

### Workflow Phases

#### 1. Initialize Phase

**Purpose**: Set up initial state for puzzle generation

**Actions**:
```python
def _initialize_node(state: AgentState) -> dict:
    # Create empty grid
    grid = CrosswordGrid(size=state.requirements.grid_size)
    
    # Update state
    return {
        "grid_state": grid.to_dict(),
        "status": "planning",
        "iteration": 0,
        "placed_words": [],
        "failed_placements": [],
    }
```

**Output**: Initial AgentState with empty grid

#### 2. Planning Phase

**Purpose**: Strategically plan word placements

**Process**:
```python
def _planner_node(state: AgentState) -> dict:
    # Analyze current grid
    analysis = planner_agent.analyze_grid_state(state)
    
    # Generate word candidates
    candidates = planner_agent.generate_word_candidates(state)
    
    # Create placement plan
    plan = planner_agent.create_placement_plan(state, candidates)
    
    # Decide action
    if planner_agent.should_stop(state):
        action = "STOP"
    else:
        action = "ADD_WORD"
    
    # Update state
    return {
        "word_candidates": candidates,
        "placement_plan": plan,
        "status": "executing" if action == "ADD_WORD" else "completed",
    }
```

**LLM Call**: Yes (GPT-4 for strategic planning)

**Output**: Updated state with word candidates and placement plan

#### 3. Execution Phase

**Purpose**: Execute placement plan by placing words

**Process**:
```python
def _executor_node(state: AgentState) -> dict:
    grid = CrosswordGrid.from_dict(state.grid_state)
    placed = []
    failed = []
    
    # Execute each placement in plan
    for plan in state.placement_plan:
        # Extract pattern
        pattern = word_generator_agent.extract_pattern(grid, plan)
        
        # Generate word
        result = word_generator_agent.generate_word(
            pattern=pattern,
            topic=state.requirements.topic,
            clue=plan.clue
        )
        
        # Validate and place
        placement = WordPlacement(
            word=result.word,
            start_row=plan.start_row,
            start_col=plan.start_col,
            direction=Direction(plan.direction),
            clue=result.clue,
            number=len(placed) + 1
        )
        
        if grid.can_place_word(placement):
            grid.place_word(placement)
            placed.append(result.word)
        else:
            failed.append({
                "word": result.word,
                "reason": "placement_conflict"
            })
    
    # Update state
    return {
        "grid_state": grid.to_dict(),
        "placed_words": state.placed_words + placed,
        "failed_placements": state.failed_placements + failed,
        "iteration": state.iteration + 1,
    }
```

**LLM Call**: Yes (GPT-4 for word generation, multiple calls)

**Output**: Updated state with new words placed on grid

#### 4. Decision Phase

**Purpose**: Determine whether to continue or end workflow

**Logic**:
```python
def _should_continue(state: AgentState) -> str:
    # Check if requirements are met
    word_count = len(state.placed_words)
    min_words = state.requirements.min_words
    max_words = state.requirements.max_words
    
    if word_count >= min_words:
        if state.status == "completed":
            return "end"
        if word_count >= max_words:
            return "end"
    
    # Check if max iterations reached
    if state.iteration >= state.max_iterations:
        return "end"
    
    # Check if planner decided to stop
    if state.status == "completed":
        return "end"
    
    # Continue planning and execution
    return "continue"
```

**Outcomes**:
- `"continue"`: Loop back to planning phase
- `"end"`: Finish workflow and return result

### Workflow Diagram

```
START
  │
  ▼
┌─────────────┐
│ Initialize  │
│ - Create    │
│   empty     │
│   grid      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Planner    │◄──────────────┐
│ - Analyze   │               │
│   grid      │               │
│ - Generate  │               │
│   candidates│               │
│ - Create    │               │
│   plan      │               │
└──────┬──────┘               │
       │                      │
       ▼                      │
┌─────────────┐               │
│  Executor   │               │
│ - Extract   │               │
│   patterns  │               │
│ - Generate  │               │
│   words     │               │
│ - Place     │               │
│   words     │               │
└──────┬──────┘               │
       │                      │
       ▼                      │
┌─────────────┐               │
│  Decision   │               │
│ - Check     │               │
│   requirements              │
│ - Check     │               │
│   iterations│               │
└──────┬──────┘               │
       │                      │
       ├──────────────────────┘
       │ continue
       │
       │ end
       ▼
      END
```

---

## State Management

### AgentState Structure

The shared state passed between agents:

```python
class AgentState(BaseModel):
    # Input requirements
    requirements: PuzzleRequirements
    
    # Grid state (serialized)
    grid_state: Optional[dict]
    
    # Word candidates and planning
    word_candidates: list[WordCandidate]
    placement_plan: list[PlacementPlan]
    
    # Execution tracking
    placed_words: list[str]
    failed_placements: list[dict]
    
    # Iteration control
    iteration: int
    max_iterations: int
    
    # Status tracking
    status: Literal["initializing", "planning", "executing", "completed", "failed"]
    error_message: Optional[str]
    
    # Metadata
    metadata: dict
```

### State Updates

Each node returns a dictionary of state updates:

```python
# Planner updates
{
    "word_candidates": [...],
    "placement_plan": [...],
    "status": "executing",
}

# Executor updates
{
    "grid_state": {...},
    "placed_words": [...],
    "failed_placements": [...],
    "iteration": iteration + 1,
}
```

LangGraph merges these updates with the existing state.

### State Serialization

The grid is serialized for LangGraph compatibility:

```python
# Serialize
grid_dict = grid.to_dict()
state.grid_state = grid_dict

# Deserialize
grid = CrosswordGrid.from_dict(state.grid_state)
```

---

## LLM Integration

### LLMClient

Wrapper around OpenAI API:

```python
class LLMClient:
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate completion from LLM"""
        
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: type[BaseModel],
    ) -> BaseModel:
        """Generate structured JSON response"""
```

### Prompt Engineering

**Planner Prompts**:
- System: Define role and objectives
- User: Provide context (topic, grid state, requirements)
- Format: Request structured JSON output

**Word Generator Prompts**:
- System: Define constraints and quality criteria
- User: Provide pattern, topic, clue, intersections
- Format: Request word with metadata

### Response Parsing

Structured outputs using Pydantic:

```python
class PlannerResponse(BaseModel):
    action: str
    reasoning: str
    word_candidates: list[dict]
    placement_plan: list[dict]

response = await llm_client.generate_json(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    response_format=PlannerResponse
)
```

### Error Handling

```python
try:
    response = await llm_client.generate_completion(...)
except OpenAIError as e:
    # Retry with exponential backoff
    await asyncio.sleep(2 ** retry_count)
    response = await llm_client.generate_completion(...)
except Exception as e:
    # Log error and continue with fallback
    logger.error(f"LLM error: {e}")
    return fallback_response
```

---

## Error Handling

### Graceful Degradation

The system handles errors gracefully:

**LLM Failures**:
- Retry with exponential backoff
- Simplify prompt and retry
- Use fallback strategies
- Continue with partial results

**Placement Failures**:
- Try alternative words
- Skip problematic placements
- Adjust strategy in next iteration
- Return best-effort puzzle

**Timeout Handling**:
- Set reasonable timeouts for LLM calls
- Cancel long-running operations
- Return partial results if timeout

### Error Recovery

```python
# Planner error recovery
try:
    candidates = await planner_agent.generate_word_candidates(state)
except LLMError:
    # Use simpler prompt
    candidates = await planner_agent.generate_simple_candidates(state)
except Exception:
    # Use fallback candidates
    candidates = get_fallback_candidates(state.requirements.topic)

# Executor error recovery
try:
    word_result = await word_generator_agent.generate_word(pattern, topic)
except LLMError:
    # Try with relaxed constraints
    word_result = await word_generator_agent.generate_word_relaxed(pattern, topic)
except Exception:
    # Skip this placement
    continue
```

### Validation

Validate all LLM outputs:

```python
def validate_word_candidate(candidate: dict) -> bool:
    # Check required fields
    if not all(k in candidate for k in ["word", "clue"]):
        return False
    
    # Validate word format
    word = candidate["word"]
    if not word.isalpha() or not word.isupper():
        return False
    
    # Validate clue
    if len(candidate["clue"]) < 5:
        return False
    
    return True
```

---

## Performance

### Optimization Strategies

**Async Operations**:
```python
# Parallel LLM calls
tasks = [
    generate_word(pattern1, topic),
    generate_word(pattern2, topic),
    generate_word(pattern3, topic),
]
results = await asyncio.gather(*tasks)
```

**Caching**:
```python
# Cache word candidates for topic
@lru_cache(maxsize=100)
def get_topic_words(topic: str) -> list[str]:
    return fetch_topic_words(topic)
```

**Batch Processing**:
```python
# Generate multiple words in one LLM call
prompt = f"""
Generate 5 words for topic '{topic}' that fit these patterns:
1. {pattern1}
2. {pattern2}
3. {pattern3}
4. {pattern4}
5. {pattern5}
"""
```

### Performance Metrics

**Typical Generation Times**:
- 8×8 grid, 10-15 words: 30-45 seconds
- 12×12 grid, 20-30 words: 60-90 seconds
- 16×16 grid, 40-50 words: 120-180 seconds

**Factors Affecting Performance**:
- Grid size (larger = slower)
- Word count (more words = more iterations)
- LLM response time (2-5 seconds per call)
- Number of retries (failures increase time)

---

## Examples

### Basic Usage

```python
from backend.agents import PuzzleOrchestrator, PuzzleGenerationRequest

# Create orchestrator
orchestrator = PuzzleOrchestrator()

# Generate puzzle
request = PuzzleGenerationRequest(
    topic="Science",
    grid_size=8,
    min_words=10,
    max_words=15,
    difficulty="medium"
)

result = await orchestrator.generate_puzzle_async(request)

if result.success:
    print(f"Generated puzzle with {result.word_count} words")
    print(f"Fill rate: {result.fill_rate}")
    print(f"Iterations: {result.iterations}")
else:
    print(f"Generation failed: {result.error_message}")
```

### Custom Agent Configuration

```python
from backend.agents import PlannerAgent, WordGeneratorAgent, CrosswordWorkflow
from backend.llm import LLMClient

# Create custom LLM client
llm_client = LLMClient(
    api_key="your-api-key",
    model="gpt-4-turbo-preview",
    temperature=0.8
)

# Create agents with custom client
planner = PlannerAgent(llm_client=llm_client)
generator = WordGeneratorAgent(llm_client=llm_client)

# Create workflow with custom agents
workflow = CrosswordWorkflow(
    planner_agent=planner,
    word_generator_agent=generator
)

# Use in orchestrator
orchestrator = PuzzleOrchestrator(workflow=workflow)
```

### Monitoring Workflow Progress

```python
# Add callback for progress monitoring
def on_iteration(state: AgentState):
    print(f"Iteration {state.iteration}:")
    print(f"  Status: {state.status}")
    print(f"  Words placed: {len(state.placed_words)}")
    print(f"  Fill rate: {state.get_fill_rate()}")

# Generate with monitoring
result = await orchestrator.generate_puzzle_async(
    request,
    on_iteration=on_iteration
)
```

---

## Best Practices

### 1. Prompt Engineering

**Be Specific**:
```python
# ❌ Vague
"Generate words for a puzzle"

# ✅ Specific
"Generate 5 science-related words that fit the pattern 'A__LE' and relate to biology"
```

**Provide Context**:
```python
# Include relevant context
prompt = f"""
Topic: {topic}
Current words: {placed_words}
Grid fill rate: {fill_rate}
Difficulty: {difficulty}

Generate words that complement existing words and maintain puzzle quality.
"""
```

### 2. Error Handling

**Always Validate LLM Outputs**:
```python
response = await llm_client.generate_json(...)
if not validate_response(response):
    # Retry or use fallback
    response = get_fallback_response()
```

**Implement Retries**:
```python
for attempt in range(max_retries):
    try:
        result = await generate_word(...)
        break
    except LLMError:
        if attempt == max_retries - 1:
            raise
        await asyncio.sleep(2 ** attempt)
```

### 3. State Management

**Keep State Serializable**:
```python
# ✅ Serializable
state.grid_state = grid.to_dict()

# ❌ Not serializable
state.grid = grid  # CrosswordGrid object
```

**Update State Immutably**:
```python
# ✅ Immutable update
return {
    "placed_words": state.placed_words + [new_word],
}

# ❌ Mutable update
state.placed_words.append(new_word)
return state
```

### 4. Testing

**Test Agents Independently**:
```python
def test_planner_agent():
    planner = PlannerAgent(llm_client=mock_llm_client)
    state = create_test_state()
    
    result = planner.generate_word_candidates(state)
    
    assert len(result) > 0
    assert all(validate_candidate(c) for c in result)
```

**Mock LLM Calls**:
```python
class MockLLMClient:
    async def generate_json(self, system_prompt, user_prompt, response_format):
        return create_mock_response(response_format)

planner = PlannerAgent(llm_client=MockLLMClient())
```

### 5. Performance

**Use Async/Await**:
```python
# ✅ Async
result = await orchestrator.generate_puzzle_async(request)

# ❌ Sync (blocks event loop)
result = orchestrator.generate_puzzle_sync(request)
```

**Batch Operations**:
```python
# Generate multiple words in parallel
tasks = [generate_word(p, topic) for p in patterns]
results = await asyncio.gather(*tasks)
```

---

## Conclusion

The AIxWord multi-agent system demonstrates how specialized AI agents can collaborate to solve complex problems. By separating strategic planning from execution and using LangGraph for orchestration, the system achieves:

- **Modularity**: Agents can be developed and tested independently
- **Flexibility**: Easy to add new agents or modify existing ones
- **Robustness**: Graceful error handling and recovery
- **Performance**: Async operations and parallel processing
- **Maintainability**: Clear separation of concerns

### Key Takeaways

1. **Multi-agent systems** enable complex problem-solving through specialization
2. **LangGraph** provides powerful workflow orchestration capabilities
3. **Iterative refinement** produces better results than single-pass generation
4. **Error handling** is critical for production-ready AI systems
5. **Prompt engineering** significantly impacts output quality

### Resources

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **OpenAI API Documentation**: https://platform.openai.com/docs/
- **Source Code**: `backend/agents/`
- **Architecture Documentation**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Documentation**: [API.md](API.md)

---

**Document Version:** 1.0.0  
**Last Updated:** September 28, 2026  
**Maintained By:** AIxWord Development Team
