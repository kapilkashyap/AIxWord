# AIxWord - Quick Start Guide

**Status:** ✅ FULLY OPERATIONAL  
**Last Updated:** 2026-09-29

---

## 🚀 Start the Application (Both Servers Already Running!)

### Backend Status
✅ **Running on:** http://localhost:8000  
✅ **PID:** 18907  
✅ **Model:** gpt-4o-mini  
✅ **API Docs:** http://localhost:8000/docs

### Frontend Status
✅ **Running on:** http://localhost:5173  
✅ **PID:** 51827  
✅ **Framework:** React + Vite

---

## 🎮 How to Use

### 1. Open the Application
Navigate to: **http://localhost:5173**

### 2. Generate a Puzzle

**Basic Generation:**
1. Enter a topic (e.g., "ocean", "space", "history", "sports")
2. Click **"Generate Puzzle"**
3. Wait 60-90 seconds for AI to create the puzzle
4. Puzzle appears with clues!

**Advanced Options:**
- **Grid Size:** 8×8 (default)
- **Max Iterations:** 1-100 (default: 50)
- Higher iterations = more words, but slower generation

### 3. Solve the Puzzle

**Manual Solving:**
- Click on a cell to select it
- Type letters (automatically uppercase)
- Use **arrow keys** to navigate
- Use **Tab** to move to next cell in word
- Use **Backspace/Delete** to clear cells

**AI Assistance:**
- **Solve Word:** Click on a clue, then "Solve This Word" button
- **Get Hint:** Click "Get Hint" for additional clues
- **Solve Puzzle:** Click "Solve Entire Puzzle" to auto-complete

---

## 🧪 Test the API Directly

### Generate a Puzzle
```bash
curl -X POST http://localhost:8000/api/puzzles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "ocean",
    "grid_size": 8,
    "max_iterations": 15
  }'
```

### Check Server Health
```bash
curl http://localhost:8000/docs
```

---

## 🔧 If You Need to Restart

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

### Both (One Command)
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

---

## 📊 Sample Puzzle Output

**Topic:** Ocean  
**Words Generated:** 9  
**Fill Rate:** ~46.9%

**ACROSS:**
1. Regular rise and fall of sea levels, influenced by the moon (TIDES)
2. A disturbance that travels through a medium (WAVE)
3. A structure formed by corals (REEF)
4. A small sheltered bay (COVE)

**DOWN:**
1. A device that increases engine efficiency (TURBO)
2. Past tense of understanding (KNEW)

---

## 💰 Cost Information

**Model:** gpt-4o-mini  
**Cost per Puzzle:** ~$0.0003 (less than 1 cent!)

**Budget Examples:**
- 100 puzzles: $0.03
- 1,000 puzzles: $0.30
- 10,000 puzzles: $3.00

---

## 🐛 Troubleshooting

### "Network Error: Unable to reach the server"
**Check if backend is running:**
```bash
ps aux | grep uvicorn | grep -v grep
```

**If not running, start it:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### "Puzzle generation failed"
**Check server logs:**
```bash
tail -f /tmp/aixword_server.log
```

**Common issues:**
- OpenAI API key not set (check `backend/.env`)
- Network blocking OpenAI API (check firewall/proxy)
- Model not available (should be using `gpt-4o-mini`)

### Frontend not loading
**Check if Vite is running:**
```bash
ps aux | grep vite | grep -v grep
```

**If not running, start it:**
```bash
cd frontend
npm run dev
```

---

## 📚 Documentation

- **Full Issue Resolution:** `ISSUE_RESOLUTION_SUMMARY.md`
- **Success Report:** `backend/PUZZLE_GENERATION_SUCCESS.md`
- **Backend README:** `backend/README.md`
- **API Documentation:** http://localhost:8000/docs
- **Architecture:** `.sasva/strategic-plans/strat_1790582429646/WORK_STRATEGY.plan.md`

---

## ✅ Verification Checklist

Before using the application, verify:

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] OpenAI API key set in `backend/.env`
- [ ] Model set to `gpt-4o-mini`
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:5173

**All checked?** You're ready to generate puzzles! 🎉

---

## 🎯 Quick Test

**1-Minute Verification:**
```bash
# Test backend
curl -X POST http://localhost:8000/api/puzzles/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","grid_size":8,"max_iterations":10}'

# Should return JSON with "success": true
```

**Expected Response:**
```json
{
  "success": true,
  "puzzle": {
    "puzzle_id": "...",
    "topic": "test",
    "grid_size": 8,
    "cells": [...],
    "clues_across": [...],
    "clues_down": [...]
  }
}
```

---

**Ready to create amazing crossword puzzles! 🎉**
