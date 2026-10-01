# AIxWord User Guide

Welcome to **AIxWord** — your AI-powered interactive crossword puzzle companion! This guide will help you get the most out of the application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Generating Puzzles](#generating-puzzles)
3. [Solving Puzzles](#solving-puzzles)
4. [AI Assistance](#ai-assistance)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Tips and Tricks](#tips-and-tricks)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What is AIxWord?

AIxWord is an interactive crossword puzzle application that uses artificial intelligence to:
- Generate custom crossword puzzles on any topic
- Provide hints when you're stuck
- Solve individual words or entire puzzles
- Validate your solutions

### System Requirements

- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)
- **Internet**: Active internet connection for puzzle generation
- **Screen**: Minimum 1024x768 resolution recommended
- **Keyboard**: For optimal navigation experience

### Accessing the Application

1. Open your web browser
2. Navigate to the application URL (e.g., `http://localhost:5173` for local development)
3. The puzzle generator will appear automatically

---

## Generating Puzzles

### Basic Puzzle Generation

1. **Enter a Topic**
   - Type any topic in the "Topic" field
   - Examples: "Space Exploration", "Ancient Rome", "Jazz Music"
   - Be specific for better results (e.g., "Marine Biology" vs. "Science")

2. **Choose Grid Size** (Optional)
   - Default: 8×8 (recommended for beginners)
   - Options: 5×5 (quick), 8×8 (standard), 10×10 (challenging), 15×15 (expert)
   - Larger grids take longer to generate

3. **Select Difficulty** (Optional)
   - **Easy**: Common words, straightforward clues
   - **Medium**: Mix of common and challenging words
   - **Hard**: Obscure words, cryptic clues

4. **Click "Generate Puzzle"**
   - Wait 30-60 seconds for generation
   - Progress updates will appear
   - Don't close the browser during generation

### Generation Tips

✅ **Do:**
- Use specific, focused topics ("Renaissance Art" not just "Art")
- Start with 8×8 grids to learn the interface
- Try different difficulty levels to find your sweet spot
- Be patient — quality puzzles take time

❌ **Don't:**
- Use extremely broad topics ("Everything", "General Knowledge")
- Expect instant results — AI generation takes time
- Generate puzzles with very obscure topics (may fail)
- Refresh the page during generation

### Understanding Generation Results

After generation, you'll see:
- **Topic**: The subject of your puzzle
- **Grid Size**: Dimensions (e.g., 8×8)
- **Word Count**: Number of words in the puzzle
- **Difficulty**: Easy, Medium, or Hard
- **Fill Rate**: Percentage of grid filled with letters

---

## Solving Puzzles

### The Puzzle Interface

Your puzzle consists of three main areas:

1. **Grid** (Left/Center)
   - Crossword grid with numbered cells
   - White cells: fillable
   - Black cells: blocked (if any)
   - Numbers indicate clue starts

2. **Clues Panel** (Right)
   - **Across**: Horizontal words
   - **Down**: Vertical words
   - Active clue is highlighted
   - Click any clue to jump to that word

3. **Controls** (Bottom)
   - Progress indicator
   - Action buttons
   - Keyboard shortcuts reference

### Entering Answers

#### Using the Mouse

1. **Click a cell** to select it
2. **Type a letter** — it appears in the cell
3. **Cursor automatically moves** to the next cell
4. **Click the same cell again** to toggle direction (across ↔ down)

#### Using the Keyboard

1. **Arrow Keys**: Navigate between cells
   - `↑` Up
   - `↓` Down
   - `←` Left
   - `→` Right

2. **Letter Keys**: Enter answers
   - Type any letter A-Z
   - Automatically converted to uppercase
   - Only one letter per cell

3. **Backspace**: Clear current cell and move back

4. **Space**: Toggle direction (across ↔ down)

5. **Tab**: Jump to next word

### Understanding Cell States

- **Selected Cell**: Blue border (your current position)
- **Active Word**: Light blue background (all cells in current word)
- **Completed Word**: Green checkmark (all letters filled)
- **Empty Cell**: White background
- **Blocked Cell**: Black background (cannot fill)

### Tracking Progress

The progress section shows:
- **Percentage Complete**: Overall completion (0-100%)
- **Filled Cells**: Number of cells you've filled
- **Completed Words**: Words that are fully filled (may not be correct)

---

## AI Assistance

AIxWord offers three types of AI assistance:

### 1. Get Hint

**When to use**: You're stuck on a word and need a nudge

**How to use**:
1. Select any cell in the word you need help with
2. Click "Get Hint" button
3. A hint appears at the top of the screen
4. Hint provides additional context or synonyms

**Example**:
- Clue: "Feline pet"
- Hint: "Think of a common household animal that meows"

### 2. Solve Word

**When to use**: You can't figure out a specific word

**How to use**:
1. Select any cell in the word you want solved
2. Click "Solve Word" button
3. AI fills in the entire word for you
4. The word is marked as AI-solved

**Note**: This reveals the answer, so use sparingly if you want the challenge!

### 3. Solve Puzzle

**When to use**: You want to see the complete solution

**How to use**:
1. Click "Solve Puzzle" button
2. Confirm you want to reveal all answers
3. AI fills in the entire grid
4. You can review the complete solution

**Note**: This ends the puzzle-solving experience. Use only when you're ready to give up or want to check answers.

### AI Assistance Tips

- **Hints are free**: Use them liberally to learn
- **Solve Word strategically**: Solve crossing words to get letters for other words
- **Solve Puzzle as last resort**: Try hints and individual word solving first
- **Learn from AI**: Pay attention to how AI solves words to improve your skills

---

## Keyboard Shortcuts

Master these shortcuts for efficient solving:

### Navigation
| Key | Action |
|-----|--------|
| `↑` | Move up |
| `↓` | Move down |
| `←` | Move left |
| `→` | Move right |
| `Tab` | Next word |
| `Shift+Tab` | Previous word |

### Input
| Key | Action |
|-----|--------|
| `A-Z` | Enter letter |
| `Backspace` | Clear cell and move back |
| `Delete` | Clear cell (stay in place) |
| `Space` | Toggle direction (across/down) |

### Actions
| Key | Action |
|-----|--------|
| `Ctrl+Z` | Undo (future feature) |
| `Ctrl+Shift+Z` | Redo (future feature) |
| `Esc` | Deselect cell |

### Pro Tips
- Keep your hands on the keyboard for fastest solving
- Use arrow keys instead of mouse for navigation
- Space bar is your friend for direction changes
- Tab through words to review your progress

---

## Tips and Tricks

### For Beginners

1. **Start with Easy Puzzles**
   - Choose "Easy" difficulty
   - Use 8×8 grid size
   - Pick familiar topics

2. **Read All Clues First**
   - Scan through all clues before starting
   - Fill in the ones you know immediately
   - Crossing letters will help with harder words

3. **Use Hints Liberally**
   - Don't be afraid to ask for hints
   - Hints help you learn patterns
   - You'll need fewer hints over time

4. **Work on Crossing Words**
   - If stuck on a word, try its crossing words
   - Each letter you fill helps with perpendicular words
   - Build up from what you know

### For Intermediate Solvers

1. **Pattern Recognition**
   - Common endings: -ING, -TION, -LY, -ED
   - Common prefixes: UN-, RE-, PRE-, DIS-
   - Use word length to narrow possibilities

2. **Strategic Hint Usage**
   - Get hints for long words (more impact)
   - Solve short crossing words to get letters
   - Use hints to break through stuck sections

3. **Validate Frequently**
   - Check your solution periodically
   - Catch mistakes early
   - Learn from incorrect answers

4. **Topic Knowledge**
   - Generate puzzles on topics you know
   - Learn new topics through puzzles
   - Use puzzles as a learning tool

### For Advanced Solvers

1. **Challenge Yourself**
   - Try "Hard" difficulty
   - Use larger grids (10×10, 15×15)
   - Avoid AI assistance until truly stuck

2. **Speed Solving**
   - Use keyboard exclusively
   - Memorize shortcuts
   - Develop a systematic approach

3. **Learn from AI**
   - When AI solves a word, understand why
   - Study the connection between clue and answer
   - Expand your vocabulary

4. **Create Themed Challenges**
   - Generate multiple puzzles on the same topic
   - Compare difficulty across topics
   - Track your improvement over time

---

## Troubleshooting

### Puzzle Generation Issues

**Problem**: "Puzzle generation failed"
- **Solution**: Try a different topic or simpler parameters
- **Reason**: Some topics are too obscure or constraints too strict

**Problem**: Generation takes too long
- **Solution**: Wait up to 90 seconds; larger grids take longer
- **Reason**: AI needs time to find valid word placements

**Problem**: Generated puzzle seems too easy/hard
- **Solution**: Adjust difficulty setting or try a different topic
- **Reason**: Difficulty varies by topic and word availability

### Solving Issues

**Problem**: Can't select a cell
- **Solution**: Click directly on the white cell area
- **Reason**: Blocked cells cannot be selected

**Problem**: Letters not appearing when typing
- **Solution**: Ensure a cell is selected (blue border)
- **Reason**: No cell is currently active

**Problem**: Can't change direction
- **Solution**: Click the same cell again or press Space
- **Reason**: Direction toggle requires explicit action

**Problem**: Keyboard shortcuts not working
- **Solution**: Click on the grid to focus it
- **Reason**: Browser focus may be elsewhere

### AI Assistance Issues

**Problem**: "Get Hint" button disabled
- **Solution**: Select a cell in a word first
- **Reason**: AI needs to know which word to hint

**Problem**: Hint doesn't help
- **Solution**: Try "Solve Word" or think about the hint differently
- **Reason**: Hints are intentionally subtle

**Problem**: AI solved word incorrectly
- **Solution**: This is rare; validate solution to check
- **Reason**: May be a bug; report if persistent

### Validation Issues

**Problem**: Validation says I'm wrong but I'm sure I'm right
- **Solution**: Check for typos or misread clues
- **Reason**: Human error is most common cause

**Problem**: Can't validate incomplete puzzle
- **Solution**: Fill in more cells; validation works on partial puzzles
- **Reason**: Validation checks filled cells only

### Browser Issues

**Problem**: Page is slow or unresponsive
- **Solution**: Refresh the page; close other tabs
- **Reason**: Browser memory or performance issues

**Problem**: Styles look broken
- **Solution**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- **Reason**: Cached CSS may be outdated

**Problem**: Can't see the full grid
- **Solution**: Zoom out (Ctrl+- or Cmd+-) or use larger screen
- **Reason**: Screen resolution too small

---

## Frequently Asked Questions

### General

**Q: Is AIxWord free to use?**
A: Yes, AIxWord is free and open-source.

**Q: Do I need to create an account?**
A: No, you can use AIxWord without registration.

**Q: Can I save my progress?**
A: Currently, progress is not saved. This feature is planned for future releases.

**Q: Can I print puzzles?**
A: Printing is not currently supported but may be added in the future.

### Puzzle Generation

**Q: How long does puzzle generation take?**
A: Typically 30-60 seconds, depending on grid size and complexity.

**Q: Can I generate puzzles on any topic?**
A: Most topics work, but very obscure or nonsensical topics may fail.

**Q: Why did my puzzle generation fail?**
A: The AI couldn't find enough valid words for your constraints. Try a different topic or easier settings.

**Q: Can I customize the clues?**
A: Not currently. The AI generates clues automatically.

### Solving

**Q: Is there a time limit?**
A: No, take as long as you need to solve the puzzle.

**Q: Can I solve puzzles offline?**
A: No, an internet connection is required for all features.

**Q: Can multiple people solve the same puzzle?**
A: Currently, puzzles are not shareable. This feature is planned.

**Q: How do I know if my answer is correct?**
A: Use the "Check Solution" button to validate your answers.

### AI Assistance

**Q: Does using AI assistance count as cheating?**
A: It's your puzzle! Use AI assistance however you like. It's a learning tool.

**Q: How accurate is the AI?**
A: Very accurate. The AI uses advanced language models for solving.

**Q: Can I turn off AI assistance?**
A: Simply don't click the AI assistance buttons. They're optional.

**Q: Will AI assistance improve my skills?**
A: Yes! Studying how AI solves words can teach you patterns and strategies.

---

## Getting Help

### Support Resources

- **Documentation**: Check this guide and ARCHITECTURE.md
- **GitHub Issues**: Report bugs or request features
- **Community**: Join discussions (if available)

### Reporting Bugs

When reporting a bug, include:
1. What you were trying to do
2. What happened instead
3. Browser and version
4. Steps to reproduce
5. Screenshots if applicable

### Feature Requests

We welcome feature requests! Consider:
- How would this improve the experience?
- Who would benefit from this feature?
- Are there workarounds currently?

---

## What's Next?

### Upcoming Features

- **Save Progress**: Resume puzzles later
- **Puzzle Library**: Browse and replay puzzles
- **Sharing**: Share puzzles with friends
- **Leaderboards**: Compete on solving time
- **Custom Clues**: Edit or write your own clues
- **Print Mode**: Print puzzles for offline solving
- **Dark Mode**: Easy on the eyes
- **Mobile App**: Native iOS and Android apps

### Learning Resources

- **Crossword Strategies**: Study classic crossword solving techniques
- **Vocabulary Building**: Expand your word knowledge
- **Pattern Recognition**: Learn common word patterns
- **Topic Exploration**: Use puzzles to learn new subjects

---

## Conclusion

Congratulations! You're now ready to master AIxWord. Remember:

- **Start simple** and work your way up
- **Use AI assistance** as a learning tool
- **Practice regularly** to improve
- **Have fun** — it's a game!

Happy puzzling! 🧩✨

---

*Last updated: September 28, 2026*
*Version: 1.0.0*
