# Real-Time Autocorrect Keyboard (Ollama + Fuzzy Matching)

This Python script provides **real-time spelling correction** for typed words by intercepting keystrokes, checking for spelling errors, and autocorrecting them using **Ollama (Mistral model) and fuzzy matching**.

## 🚀 Features
- **Live Keystroke Capture**: Uses `pynput` to track key presses.
- **Automated Spell Correction**: Sends words to **Ollama** for correction.
- **Fuzzy Matching**: Ensures only similar words are replaced.
- **Seamless Typing Experience**: Backspaces incorrect words and types corrected versions automatically.
- **Handles Inactivity**: If typing stops for **0.9 seconds**, it auto-processes the last word.

## 📜 Requirements
- Python 3.8+
- `pynput` (for keyboard listening)
- `fuzzywuzzy` (for word similarity check)
- `requests` (for API calls)
- **Ollama installed and running** (For Mistral model-based corrections)

### Install Dependencies:
```bash
pip install pynput fuzzywuzzy requests
  
