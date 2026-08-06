# Agentic Cocktail Review

A Python application that extracts structured cocktail recipes from PDF
documents, validates the results using deterministic rules, stores the
results in SQLite, and routes uncertain extractions to human review.

## Features

- PDF text extraction
- Structured LLM output
- Pydantic validation
- Unit normalization
- Deterministic business rules
- SQLite persistence
- Human-review queue
- Automated tests

## Architecture

1. Load a PDF document
2. Extract cocktail fields using Claude
3. Normalize and validate the extraction
4. Save the result
5. Route warnings and uncertain results to human review

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
