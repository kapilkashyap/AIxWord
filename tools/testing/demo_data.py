"""
Demo data generator for AIxWord application.

This module provides pre-generated puzzle data for demonstrations, testing,
and quick starts. It includes complete puzzles with solutions that can be
used without requiring OpenAI API calls.

Features:
- Pre-generated puzzles on various topics
- Complete with clues, solutions, and metadata
- Useful for demos, testing, and offline development
- Matches the production data format exactly

Usage:
    from backend.demo_data import get_demo_puzzle, list_demo_topics
    
    # Get a demo puzzle
    puzzle = get_demo_puzzle('science')
    
    # List available topics
    topics = list_demo_topics()
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

try:
    # Try relative imports first (when run as module)
    from backend.domain.models import Direction, Cell, Clue
    from backend.domain.grid import CrosswordGrid
    from backend.api.models import StoredPuzzle, PuzzleMetadata
except ImportError:
    # Fall back to absolute imports (when run standalone)
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from domain.models import Direction, Cell, Clue
    from domain.grid import CrosswordGrid
    from api.models import StoredPuzzle, PuzzleMetadata


# ============================================================================
# Demo Puzzle Data
# ============================================================================

DEMO_PUZZLES = {
    "science": {
        "topic": "Science",
        "grid_size": 8,
        "difficulty": "medium",
        "words": [
            # Across words
            {"word": "ATOM", "clue": "Smallest unit of matter", "row": 0, "col": 0, "direction": "across", "number": 1},
            {"word": "CELL", "clue": "Basic unit of life", "row": 0, "col": 5, "direction": "across", "number": 2},
            {"word": "ENERGY", "clue": "Capacity to do work", "row": 2, "col": 0, "direction": "across", "number": 5},
            {"word": "GENE", "clue": "Unit of heredity", "row": 2, "col": 7, "direction": "across", "number": 6},
            {"word": "LASER", "clue": "Focused beam of light", "row": 4, "col": 0, "direction": "across", "number": 9},
            {"word": "ORBIT", "clue": "Path around a celestial body", "row": 6, "col": 0, "direction": "across", "number": 12},
            {"word": "WAVE", "clue": "Oscillating disturbance", "row": 6, "col": 6, "direction": "across", "number": 13},
            # Down words
            {"word": "ACID", "clue": "pH less than 7", "row": 0, "col": 0, "direction": "down", "number": 1},
            {"word": "TESLA", "clue": "Unit of magnetic field", "row": 0, "col": 2, "direction": "down", "number": 3},
            {"word": "MOLECULE", "clue": "Group of bonded atoms", "row": 0, "col": 3, "direction": "down", "number": 4},
            {"word": "ELECTRON", "clue": "Negatively charged particle", "row": 2, "col": 1, "direction": "down", "number": 7},
            {"word": "GRAVITY", "clue": "Force of attraction", "row": 2, "col": 5, "direction": "down", "number": 8},
            {"word": "NEUTRON", "clue": "Neutral subatomic particle", "row": 2, "col": 7, "direction": "down", "number": 10},
            {"word": "PROTON", "clue": "Positively charged particle", "row": 4, "col": 4, "direction": "down", "number": 11},
        ],
    },
    "history": {
        "topic": "History",
        "grid_size": 8,
        "difficulty": "medium",
        "words": [
            # Across words
            {"word": "ROME", "clue": "Ancient empire capital", "row": 0, "col": 0, "direction": "across", "number": 1},
            {"word": "EGYPT", "clue": "Land of pyramids", "row": 0, "col": 5, "direction": "across", "number": 2},
            {"word": "EMPIRE", "clue": "Large political unit", "row": 2, "col": 0, "direction": "across", "number": 5},
            {"word": "KING", "clue": "Male monarch", "row": 2, "col": 7, "direction": "across", "number": 6},
            {"word": "TREATY", "clue": "Formal agreement", "row": 4, "col": 0, "direction": "across", "number": 9},
            {"word": "BATTLE", "clue": "Military engagement", "row": 6, "col": 0, "direction": "across", "number": 12},
            {"word": "WAR", "clue": "Armed conflict", "row": 6, "col": 7, "direction": "across", "number": 13},
            # Down words
            {"word": "REVOLUTION", "clue": "Overthrow of government", "row": 0, "col": 0, "direction": "down", "number": 1},
            {"word": "MEDIEVAL", "clue": "Middle Ages period", "row": 0, "col": 2, "direction": "down", "number": 3},
            {"word": "EMPEROR", "clue": "Supreme ruler", "row": 0, "col": 3, "direction": "down", "number": 4},
            {"word": "PHARAOH", "clue": "Egyptian ruler", "row": 2, "col": 1, "direction": "down", "number": 7},
            {"word": "DYNASTY", "clue": "Ruling family line", "row": 2, "col": 5, "direction": "down", "number": 8},
            {"word": "KNIGHT", "clue": "Medieval warrior", "row": 2, "col": 7, "direction": "down", "number": 10},
            {"word": "CASTLE", "clue": "Fortified residence", "row": 4, "col": 4, "direction": "down", "number": 11},
        ],
    },
    "technology": {
        "topic": "Technology",
        "grid_size": 8,
        "difficulty": "medium",
        "words": [
            # Across words
            {"word": "CODE", "clue": "Programming instructions", "row": 0, "col": 0, "direction": "across", "number": 1},
            {"word": "DATA", "clue": "Information in digital form", "row": 0, "col": 5, "direction": "across", "number": 2},
            {"word": "NETWORK", "clue": "Connected computers", "row": 2, "col": 0, "direction": "across", "number": 5},
            {"word": "CHIP", "clue": "Integrated circuit", "row": 2, "col": 8, "direction": "across", "number": 6},
            {"word": "SERVER", "clue": "Computer providing services", "row": 4, "col": 0, "direction": "across", "number": 9},
            {"word": "ROUTER", "clue": "Network traffic director", "row": 6, "col": 0, "direction": "across", "number": 12},
            {"word": "WEB", "clue": "Internet information system", "row": 6, "col": 7, "direction": "across", "number": 13},
            # Down words
            {"word": "CLOUD", "clue": "Remote computing service", "row": 0, "col": 0, "direction": "down", "number": 1},
            {"word": "DIGITAL", "clue": "Binary representation", "row": 0, "col": 2, "direction": "down", "number": 3},
            {"word": "ETHERNET", "clue": "LAN technology", "row": 0, "col": 3, "direction": "down", "number": 4},
            {"word": "WIRELESS", "clue": "No physical connection", "row": 2, "col": 1, "direction": "down", "number": 7},
            {"word": "INTERNET", "clue": "Global network", "row": 2, "col": 5, "direction": "down", "number": 8},
            {"word": "PROTOCOL", "clue": "Communication rules", "row": 2, "col": 8, "direction": "down", "number": 10},
            {"word": "VIRTUAL", "clue": "Simulated by software", "row": 4, "col": 4, "direction": "down", "number": 11},
        ],
    },
    "nature": {
        "topic": "Nature",
        "grid_size": 8,
        "difficulty": "easy",
        "words": [
            # Across words
            {"word": "TREE", "clue": "Woody plant", "row": 0, "col": 0, "direction": "across", "number": 1},
            {"word": "LEAF", "clue": "Plant's photosynthesis organ", "row": 0, "col": 5, "direction": "across", "number": 2},
            {"word": "FOREST", "clue": "Dense woodland", "row": 2, "col": 0, "direction": "across", "number": 5},
            {"word": "BIRD", "clue": "Feathered animal", "row": 2, "col": 7, "direction": "across", "number": 6},
            {"word": "OCEAN", "clue": "Large body of salt water", "row": 4, "col": 0, "direction": "across", "number": 9},
            {"word": "RIVER", "clue": "Flowing water body", "row": 6, "col": 0, "direction": "across", "number": 12},
            {"word": "RAIN", "clue": "Water falling from clouds", "row": 6, "col": 6, "direction": "across", "number": 13},
            # Down words
            {"word": "TIGER", "clue": "Striped big cat", "row": 0, "col": 0, "direction": "down", "number": 1},
            {"word": "EAGLE", "clue": "Large bird of prey", "row": 0, "col": 2, "direction": "down", "number": 3},
            {"word": "ELEPHANT", "clue": "Largest land animal", "row": 0, "col": 3, "direction": "down", "number": 4},
            {"word": "FLOWER", "clue": "Plant's reproductive structure", "row": 2, "col": 1, "direction": "down", "number": 7},
            {"word": "STREAM", "clue": "Small flowing water", "row": 2, "col": 5, "direction": "down", "number": 8},
            {"word": "DOLPHIN", "clue": "Intelligent marine mammal", "row": 2, "col": 7, "direction": "down", "number": 10},
            {"word": "CORAL", "clue": "Marine invertebrate", "row": 4, "col": 4, "direction": "down", "number": 11},
        ],
    },
}


# ============================================================================
# Helper Functions
# ============================================================================

def _create_grid_from_words(grid_size: int, words: List[Dict]) -> CrosswordGrid:
    """
    Create a CrosswordGrid from word placement data.
    
    Args:
        grid_size: Size of the grid (NxN)
        words: List of word placement dictionaries
        
    Returns:
        CrosswordGrid instance with words placed
    """
    grid = CrosswordGrid(size=grid_size)
    
    # Place all words
    for word_data in words:
        word = word_data["word"]
        clue_text = word_data["clue"]
        row = word_data["row"]
        col = word_data["col"]
        direction = Direction(word_data["direction"])
        number = word_data["number"]
        
        # Create clue
        clue = Clue(
            number=number,
            direction=direction,
            text=clue_text,
            answer=word,
            row=row,
            col=col,
            length=len(word),
        )
        
        # Place word on grid
        for i, letter in enumerate(word):
            if direction == Direction.ACROSS:
                cell_row, cell_col = row, col + i
            else:
                cell_row, cell_col = row + i, col
            
            # Get or create cell
            cell = grid.get_cell(cell_row, cell_col)
            if cell is None:
                cell = Cell(row=cell_row, col=cell_col, value=letter)
                grid.cells[cell_row * grid_size + cell_col] = cell
            else:
                cell.value = letter
            
            # Set clue number on first cell
            if i == 0:
                cell.number = number
        
        # Add clue to grid
        grid.clues.append(clue)
        
        # Track placement
        try:
            from backend.domain.word import WordPlacement
        except ImportError:
            from domain.word import WordPlacement
        placement = WordPlacement(
            word=word,
            clue=clue_text,
            start_row=row,
            start_col=col,
            direction=direction,
            number=number,
        )
        grid.placements.append(placement)
    
    return grid


def get_demo_puzzle(topic: str) -> Optional[StoredPuzzle]:
    """
    Get a pre-generated demo puzzle by topic.
    
    Args:
        topic: Topic name (case-insensitive)
        
    Returns:
        StoredPuzzle instance or None if topic not found
        
    Example:
        >>> puzzle = get_demo_puzzle('science')
        >>> print(puzzle.metadata.topic)
        Science
    """
    topic_key = topic.lower()
    
    if topic_key not in DEMO_PUZZLES:
        return None
    
    demo_data = DEMO_PUZZLES[topic_key]
    
    # Create grid from word data
    grid = _create_grid_from_words(
        grid_size=demo_data["grid_size"],
        words=demo_data["words"],
    )
    
    # Create stored puzzle
    puzzle = StoredPuzzle.from_grid(
        grid=grid,
        topic=demo_data["topic"],
        difficulty=demo_data["difficulty"],
        iterations=1,  # Demo puzzles are pre-made
        puzzle_id=str(uuid.uuid4()),
    )
    
    return puzzle


def list_demo_topics() -> List[str]:
    """
    Get list of available demo puzzle topics.
    
    Returns:
        List of topic names
        
    Example:
        >>> topics = list_demo_topics()
        >>> print(topics)
        ['Science', 'History', 'Technology', 'Nature']
    """
    return [data["topic"] for data in DEMO_PUZZLES.values()]


def get_all_demo_puzzles() -> Dict[str, StoredPuzzle]:
    """
    Get all demo puzzles as a dictionary.
    
    Returns:
        Dictionary mapping topic keys to StoredPuzzle instances
        
    Example:
        >>> puzzles = get_all_demo_puzzles()
        >>> for topic, puzzle in puzzles.items():
        ...     print(f"{topic}: {puzzle.metadata.word_count} words")
    """
    return {
        topic: get_demo_puzzle(topic)
        for topic in DEMO_PUZZLES.keys()
        if get_demo_puzzle(topic) is not None
    }


def is_demo_topic(topic: str) -> bool:
    """
    Check if a topic has demo data available.
    
    Args:
        topic: Topic name (case-insensitive)
        
    Returns:
        True if demo data exists for this topic
        
    Example:
        >>> is_demo_topic('science')
        True
        >>> is_demo_topic('unknown')
        False
    """
    return topic.lower() in DEMO_PUZZLES


# ============================================================================
# Demo Data Statistics
# ============================================================================

def get_demo_stats() -> Dict[str, any]:
    """
    Get statistics about available demo data.
    
    Returns:
        Dictionary with demo data statistics
        
    Example:
        >>> stats = get_demo_stats()
        >>> print(f"Total puzzles: {stats['total_puzzles']}")
    """
    puzzles = get_all_demo_puzzles()
    
    total_words = sum(
        len(data["words"]) for data in DEMO_PUZZLES.values()
    )
    
    return {
        "total_puzzles": len(puzzles),
        "topics": list_demo_topics(),
        "total_words": total_words,
        "average_words_per_puzzle": total_words / len(puzzles) if puzzles else 0,
        "grid_sizes": list(set(data["grid_size"] for data in DEMO_PUZZLES.values())),
        "difficulties": list(set(data["difficulty"] for data in DEMO_PUZZLES.values())),
    }


# ============================================================================
# Main (for testing)
# ============================================================================

if __name__ == "__main__":
    print("AIxWord Demo Data")
    print("=" * 60)
    
    # Show statistics
    stats = get_demo_stats()
    print(f"\nAvailable Demo Puzzles: {stats['total_puzzles']}")
    print(f"Topics: {', '.join(stats['topics'])}")
    print(f"Total Words: {stats['total_words']}")
    print(f"Average Words per Puzzle: {stats['average_words_per_puzzle']:.1f}")
    
    # Show each puzzle
    print("\n" + "=" * 60)
    for topic in list_demo_topics():
        puzzle = get_demo_puzzle(topic)
        if puzzle:
            print(f"\n{topic}:")
            print(f"  Grid Size: {puzzle.metadata.grid_size}x{puzzle.metadata.grid_size}")
            print(f"  Difficulty: {puzzle.metadata.difficulty}")
            print(f"  Word Count: {puzzle.metadata.word_count}")
            print(f"  Fill Rate: {puzzle.metadata.fill_rate:.1%}")
            print(f"  Clues: {len(puzzle.clues)}")
    
    print("\n" + "=" * 60)
    print("\nUsage:")
    print("  from backend.demo_data import get_demo_puzzle")
    print("  puzzle = get_demo_puzzle('science')")
    print("=" * 60)
