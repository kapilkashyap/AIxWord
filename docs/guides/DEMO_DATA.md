# Demo Data Guide

**Version:** 1.0.0  
**Last Updated:** September 29, 2026  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Available Demo Puzzles](#available-demo-puzzles)
3. [Using Demo Data](#using-demo-data)
4. [API Integration](#api-integration)
5. [Demo Data Structure](#demo-data-structure)
6. [Benefits](#benefits)
7. [Limitations](#limitations)
8. [Extending Demo Data](#extending-demo-data)

---

## Overview

The AIxWord application includes pre-generated demo puzzles that can be used for:

- **Quick demonstrations** without waiting for AI generation
- **Testing and development** without consuming OpenAI API credits
- **Offline development** when API access is unavailable
- **Educational examples** showing puzzle structure and quality
- **Performance benchmarking** with consistent data

Demo puzzles are complete, valid crossword puzzles with clues and solutions that match the exact format of AI-generated puzzles.

### Key Features

✅ **No API Required** - Use puzzles without OpenAI API calls  
✅ **Instant Access** - No generation delay (< 1ms)  
✅ **High Quality** - Hand-crafted, coherent puzzles  
✅ **Multiple Topics** - Science, History, Technology, Nature  
✅ **Production Format** - Identical to AI-generated puzzles  
✅ **Fully Solvable** - Complete with clues and solutions

---

## Available Demo Puzzles

### 1. Science Puzzle

**Topic:** Science  
**Grid Size:** 8×8  
**Difficulty:** Medium  
**Word Count:** 14 words  
**Themes:** Physics, Chemistry, Biology

**Sample Words:**
- ATOM - Smallest unit of matter
- ENERGY - Capacity to do work
- MOLECULE - Group of bonded atoms
- ELECTRON - Negatively charged particle
- GRAVITY - Force of attraction

**Use Cases:**
- STEM education demonstrations
- Physics/chemistry vocabulary learning
- Science quiz applications

---

### 2. History Puzzle

**Topic:** History  
**Grid Size:** 8×8  
**Difficulty:** Medium  
**Word Count:** 14 words  
**Themes:** Ancient civilizations, Medieval period, Warfare

**Sample Words:**
- ROME - Ancient empire capital
- EMPIRE - Large political unit
- REVOLUTION - Overthrow of government
- PHARAOH - Egyptian ruler
- DYNASTY - Ruling family line

**Use Cases:**
- History education
- Social studies curriculum
- Historical trivia games

---

### 3. Technology Puzzle

**Topic:** Technology  
**Grid Size:** 8×8  
**Difficulty:** Medium  
**Word Count:** 14 words  
**Themes:** Computing, Networking, Internet

**Sample Words:**
- CODE - Programming instructions
- NETWORK - Connected computers
- CLOUD - Remote computing service
- INTERNET - Global network
- PROTOCOL - Communication rules

**Use Cases:**
- Computer science education
- IT training materials
- Tech vocabulary building

---

### 4. Nature Puzzle

**Topic:** Nature  
**Grid Size:** 8×8  
**Difficulty:** Easy  
**Word Count:** 14 words  
**Themes:** Animals, Plants, Ecosystems

**Sample Words:**
- TREE - Woody plant
- FOREST - Dense woodland
- TIGER - Striped big cat
- ELEPHANT - Largest land animal
- OCEAN - Large body of salt water

**Use Cases:**
- Environmental education
- Biology lessons
- Nature vocabulary for children

---

## Using Demo Data

### Python Backend

#### Get a Single Demo Puzzle

```python
from backend.demo_data import get_demo_puzzle

# Get science puzzle
puzzle = get_demo_puzzle('science')

if puzzle:
    print(f"Topic: {puzzle.metadata.topic}")
    print(f"Words: {puzzle.metadata.word_count}")
    print(f"Fill Rate: {puzzle.metadata.fill_rate:.1%}")
```

#### List Available Topics

```python
from backend.demo_data import list_demo_topics

topics = list_demo_topics()
print(f"Available topics: {', '.join(topics)}")
# Output: Available topics: Science, History, Technology, Nature
```

#### Check if Topic Has Demo Data

```python
from backend.demo_data import is_demo_topic

if is_demo_topic('science'):
    print("Science demo available!")
else:
    print("No demo for this topic")
```

#### Get All Demo Puzzles

```python
from backend.demo_data import get_all_demo_puzzles

puzzles = get_all_demo_puzzles()
for topic, puzzle in puzzles.items():
    print(f"{topic}: {puzzle.metadata.word_count} words")
```

#### Get Demo Statistics

```python
from backend.demo_data import get_demo_stats

stats = get_demo_stats()
print(f"Total puzzles: {stats['total_puzzles']}")
print(f"Total words: {stats['total_words']}")
print(f"Average words: {stats['average_words_per_puzzle']:.1f}")
```

---

## API Integration

### Using Demo Data in API Endpoints

Demo puzzles can be integrated into the API to provide instant puzzle access:

```python
from fastapi import APIRouter
from backend.demo_data import get_demo_puzzle, list_demo_topics

router = APIRouter()

@router.get("/api/demo/topics")
async def get_demo_topics():
    """Get list of available demo topics."""
    return {"topics": list_demo_topics()}

@router.get("/api/demo/puzzle/{topic}")
async def get_demo_puzzle_endpoint(topic: str):
    """Get a demo puzzle by topic."""
    puzzle = get_demo_puzzle(topic)
    if not puzzle:
        raise HTTPException(status_code=404, detail="Demo topic not found")
    return puzzle.to_dict()
```

### Frontend Integration

```typescript
// Fetch demo topics
const response = await fetch('/api/demo/topics');
const { topics } = await response.json();

// Fetch specific demo puzzle
const puzzleResponse = await fetch('/api/demo/puzzle/science');
const puzzle = await puzzleResponse.json();
```

---

## Demo Data Structure

### Puzzle Format

Each demo puzzle includes:

```python
{
    "topic": "Science",           # Puzzle topic
    "grid_size": 8,               # Grid dimensions (8×8)
    "difficulty": "medium",       # Difficulty level
    "words": [                    # List of word placements
        {
            "word": "ATOM",       # The word
            "clue": "Smallest unit of matter",  # Clue text
            "row": 0,             # Starting row
            "col": 0,             # Starting column
            "direction": "across", # Direction (across/down)
            "number": 1           # Clue number
        },
        # ... more words
    ]
}
```

### Grid Representation

Demo puzzles are converted to `CrosswordGrid` objects with:

- **Cells**: Individual grid cells with letters
- **Clues**: Across and down clues with answers
- **Placements**: Word placement information
- **Metadata**: Topic, difficulty, statistics

### Storage Format

Demo puzzles are stored as `StoredPuzzle` objects:

```python
StoredPuzzle(
    metadata=PuzzleMetadata(
        id="uuid",
        topic="Science",
        grid_size=8,
        difficulty="medium",
        word_count=14,
        fill_rate=0.75,
        iterations=1,
        status="completed"
    ),
    grid_data={...},
    clues=[...],
    solution={...}
)
```

---

## Benefits

### 1. Development Speed

**Without Demo Data:**
- Wait 30-60 seconds for each puzzle generation
- Consume API credits for every test
- Require internet connection

**With Demo Data:**
- Instant puzzle access (< 1ms)
- Zero API costs
- Work offline

### 2. Consistent Testing

- Same puzzles every time
- Reproducible test results
- Predictable behavior
- Easy debugging

### 3. Cost Savings

- No OpenAI API calls for demos
- Preserve API credits for production
- Free for development and testing

### 4. Educational Value

- Study well-formed puzzle structure
- Learn clue writing techniques
- Understand grid patterns
- Reference implementation examples

### 5. User Experience

- Instant "Try Demo" functionality
- No wait time for first impression
- Reliable demo experience
- Showcase app capabilities immediately

---

## Limitations

### What Demo Data Is NOT

❌ **Not AI-Generated** - Hand-crafted, not from LLM  
❌ **Limited Topics** - Only 4 topics available  
❌ **Fixed Content** - Same puzzles every time  
❌ **No Customization** - Cannot adjust parameters  
❌ **No RAG Integration** - Not based on documents

### When to Use AI Generation Instead

Use AI generation when you need:
- Custom topics beyond the 4 demo topics
- Unique puzzles for each user
- Document-based puzzle generation (RAG)
- Variable difficulty levels
- Different grid sizes
- Fresh content for repeat users

---

## Extending Demo Data

### Adding New Demo Puzzles

To add a new demo puzzle, edit `backend/demo_data.py`:

```python
DEMO_PUZZLES = {
    # ... existing puzzles ...
    
    "sports": {
        "topic": "Sports",
        "grid_size": 8,
        "difficulty": "easy",
        "words": [
            {
                "word": "SOCCER",
                "clue": "Football played with feet",
                "row": 0,
                "col": 0,
                "direction": "across",
                "number": 1
            },
            # ... more words
        ],
    },
}
```

### Design Guidelines

When creating demo puzzles:

1. **Grid Size**: Use 8×8 for consistency
2. **Word Count**: Aim for 12-16 words
3. **Fill Rate**: Target 60-80% grid coverage
4. **Clue Quality**: Clear, unambiguous clues
5. **Word Intersections**: Ensure proper crossings
6. **Difficulty Balance**: Mix easy and hard words
7. **Topic Coherence**: All words relate to topic
8. **No Obscure Words**: Use common vocabulary

### Validation Checklist

Before adding a demo puzzle:

- [ ] All words intersect correctly
- [ ] No isolated words or sections
- [ ] Clues are clear and accurate
- [ ] Grid is properly filled
- [ ] No spelling errors
- [ ] Appropriate difficulty level
- [ ] Topic-relevant vocabulary
- [ ] Proper numbering sequence

---

## Use Cases

### 1. Quick Start Tutorial

```python
# Show new users a demo puzzle immediately
demo_puzzle = get_demo_puzzle('nature')  # Easy puzzle
# Display to user without waiting
```

### 2. Automated Testing

```python
# Use consistent demo data in tests
def test_puzzle_validation():
    puzzle = get_demo_puzzle('science')
    assert puzzle.metadata.word_count == 14
    assert puzzle.metadata.grid_size == 8
```

### 3. Performance Benchmarking

```python
# Measure solving performance with known puzzles
import time

puzzle = get_demo_puzzle('technology')
start = time.time()
result = solve_puzzle(puzzle)
duration = time.time() - start
print(f"Solved in {duration:.2f}s")
```

### 4. Offline Development

```python
# Work without internet/API access
if not api_available():
    puzzle = get_demo_puzzle('history')
else:
    puzzle = generate_puzzle_with_ai(topic)
```

### 5. Educational Demonstrations

```python
# Show puzzle structure to students
puzzle = get_demo_puzzle('science')
print("Across Clues:")
for clue in puzzle.clues:
    if clue.direction == "across":
        print(f"  {clue.number}. {clue.text}")
```

---

## API Reference

### Functions

#### `get_demo_puzzle(topic: str) -> Optional[StoredPuzzle]`

Get a demo puzzle by topic (case-insensitive).

**Parameters:**
- `topic` (str): Topic name ('science', 'history', 'technology', 'nature')

**Returns:**
- `StoredPuzzle` or `None` if topic not found

**Example:**
```python
puzzle = get_demo_puzzle('science')
```

---

#### `list_demo_topics() -> List[str]`

Get list of available demo topics.

**Returns:**
- List of topic names

**Example:**
```python
topics = list_demo_topics()
# ['Science', 'History', 'Technology', 'Nature']
```

---

#### `get_all_demo_puzzles() -> Dict[str, StoredPuzzle]`

Get all demo puzzles as a dictionary.

**Returns:**
- Dictionary mapping topic keys to puzzles

**Example:**
```python
puzzles = get_all_demo_puzzles()
for topic, puzzle in puzzles.items():
    print(f"{topic}: {puzzle.metadata.word_count} words")
```

---

#### `is_demo_topic(topic: str) -> bool`

Check if a topic has demo data.

**Parameters:**
- `topic` (str): Topic name (case-insensitive)

**Returns:**
- `True` if demo exists, `False` otherwise

**Example:**
```python
if is_demo_topic('science'):
    print("Demo available!")
```

---

#### `get_demo_stats() -> Dict[str, any]`

Get statistics about demo data.

**Returns:**
- Dictionary with statistics

**Example:**
```python
stats = get_demo_stats()
print(f"Total puzzles: {stats['total_puzzles']}")
```

---

## Testing Demo Data

### Run Demo Data Script

```bash
cd backend
python demo_data.py
```

**Expected Output:**
```
AIxWord Demo Data
============================================================

Available Demo Puzzles: 4
Topics: Science, History, Technology, Nature
Total Words: 56
Average Words per Puzzle: 14.0

============================================================

Science:
  Grid Size: 8x8
  Difficulty: medium
  Word Count: 14
  Fill Rate: 75.0%
  Clues: 14

History:
  Grid Size: 8x8
  Difficulty: medium
  Word Count: 14
  Fill Rate: 75.0%
  Clues: 14

...
```

### Integration Test

```python
import pytest
from backend.demo_data import get_demo_puzzle, list_demo_topics

def test_demo_puzzles_exist():
    """Test that all demo puzzles can be loaded."""
    topics = list_demo_topics()
    assert len(topics) > 0
    
    for topic in topics:
        puzzle = get_demo_puzzle(topic.lower())
        assert puzzle is not None
        assert puzzle.metadata.word_count > 0
        assert len(puzzle.clues) > 0

def test_demo_puzzle_structure():
    """Test that demo puzzles have correct structure."""
    puzzle = get_demo_puzzle('science')
    
    assert puzzle.metadata.topic == "Science"
    assert puzzle.metadata.grid_size == 8
    assert puzzle.metadata.word_count == 14
    assert len(puzzle.clues) == 14
```

---

## Best Practices

### When to Use Demo Data

✅ **DO use demo data for:**
- Initial app demonstrations
- Development and testing
- Performance benchmarking
- Educational examples
- Offline development
- API credit conservation

❌ **DON'T use demo data for:**
- Production user experiences (after first demo)
- Custom topic requirements
- Document-based puzzles
- Unique content needs
- Variable difficulty testing

### Combining Demo and AI

```python
def get_puzzle(topic: str, use_demo: bool = False):
    """Get puzzle with fallback to demo."""
    if use_demo or is_demo_topic(topic):
        demo = get_demo_puzzle(topic)
        if demo:
            return demo
    
    # Fall back to AI generation
    return generate_puzzle_with_ai(topic)
```

---

## Troubleshooting

### Demo Puzzle Not Loading

**Problem:** `get_demo_puzzle()` returns `None`

**Solutions:**
1. Check topic name (case-insensitive)
2. Verify topic exists: `list_demo_topics()`
3. Ensure `demo_data.py` is in Python path

### Import Errors

**Problem:** Cannot import `demo_data`

**Solutions:**
```bash
# Ensure backend is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/AIxWord"

# Or install in development mode
cd backend
pip install -e .
```

### Grid Structure Issues

**Problem:** Demo puzzle grid doesn't display correctly

**Solutions:**
1. Verify grid size matches data
2. Check cell coordinates are valid
3. Ensure word intersections are correct

---

## Future Enhancements

### Planned Features

- [ ] More demo topics (10+ total)
- [ ] Multiple difficulty levels per topic
- [ ] Larger grid sizes (10×10, 12×12)
- [ ] Themed puzzle collections
- [ ] Seasonal/holiday puzzles
- [ ] Multi-language support
- [ ] Export to standard formats

### Community Contributions

Want to contribute demo puzzles? See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## Summary

Demo data provides:

- **4 high-quality puzzles** on popular topics
- **Instant access** without API calls
- **Perfect for demos** and development
- **Consistent testing** data
- **Educational examples** of puzzle structure

Use demo data to:
- Showcase app capabilities immediately
- Develop and test without API costs
- Work offline
- Learn puzzle structure
- Benchmark performance

For production use with custom topics, use AI generation.

---

## Related Documentation

- **[User Guide](USER_GUIDE.md)** - Using the application
- **[API Reference](API.md)** - API endpoints
- **[Architecture](ARCHITECTURE.md)** - System design
- **[Quick Start](QUICK_START_GUIDE.md)** - Getting started

---

**Version:** 1.0.0  
**Last Updated:** September 29, 2026  
**Maintained By:** AIxWord Development Team

---

*For questions or issues with demo data, see [Troubleshooting](#troubleshooting) or consult the [User Guide](USER_GUIDE.md).*
