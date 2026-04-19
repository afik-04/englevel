# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Telegram bot for English proficiency testing. Users take a multiple-choice quiz and receive a CEFR level (A1–C1) based on their score. Built with Python, comments and user-facing strings are in Russian.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot (polling mode)
python main.py

# Run tests (no tests exist yet; pytest is configured)
pytest
pytest --cov    # with coverage
```

Note: `requirements.txt` is UTF-16 LE encoded.

## Architecture

**Bot runtime**: `python-telegram-bot` 22.7 (async). Django is configured in `config/` but not actively used by the bot.

**Entry point**: `main.py` — loads `.env`, builds the Telegram Application, registers handlers, starts polling.

**Handler flow** (`bot/handlers.py`):
- `/start` → welcome message with main keyboard
- `/test` → creates in-memory session in `user_sessions` dict, sends first question
- Callback queries → `handle_answer()` checks answer, advances to next question or calls `finish_test()`
- `finish_test()` calculates percentage, maps to CEFR level, cleans up session

**Keyboards** (`bot/keyboards.py`): `get_main_keyboard()` (reply buttons) and `get_question_keyboard()` (inline answer buttons).

**Question bank** (`questions.py`): list of dicts with `text`, `options`, `correct` (index), `level`. Currently only 2 of 10 planned questions.

**State**: User sessions are stored in a Python dict — no persistence across restarts. No database integration yet (commented as TODO).

## Known Incomplete Features

- `/result` and `/help` commands are shown in the keyboard but not implemented
- Only 2 questions defined; code comments indicate 10 are planned
- Database persistence for results is planned but not built
