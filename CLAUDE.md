# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```powershell
# Activate the existing venv (already present at .venv/)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure env
copy .env.example .env   # then fill in GROQ_API_KEY
```

## Running the pipeline

```powershell
# Chunk reviews into documents/chunks.json
python text_chunker.py
```

## Project overview

This is an AI201 RAG (Retrieval-Augmented Generation) pipeline over student reviews of CCNY Math professors scraped from RateMyProfessors. The pipeline has five stages:

1. **Ingestion** — raw reviews live in `documents/reviews.txt`, formatted as blocks separated by `---`. Each block has a header line (`Professor | Course | Rating | Difficulty`), a `Tags:` line, and a `Review:` line.

2. **Chunking** (`text_chunker.py`) — splits on `---` delimiters (one review = one chunk). Outputs `documents/chunks.json`: a list of dicts with `chunk_id`, `text`, `professor`, `course`, `rating`, `difficulty`.

3. **Embedding + vector store** — planned: `sentence-transformers` (`all-MiniLM-L6-v2`) + `chromadb`.

4. **Retrieval** — planned: top-k=10 semantic search over the ChromaDB collection.

5. **Generation** — planned: Groq LLM (key via `GROQ_API_KEY` in `.env`) with a grounded system prompt that restricts answers to retrieved chunks.

## Key files

| File | Purpose |
|------|---------|
| `planning.md` | Spec: chunking rationale, retrieval design, 5 eval questions, architecture diagram |
| `text_chunker.py` | Stage 2 — paragraph chunker, writes `documents/chunks.json` |
| `documents/reviews.txt` | Raw source data (~781 reviews) |
| `documents/chunks.json` | Output of chunker, input to embedder |
| `README.md` | Submission template — fill in after each milestone |

## Env vars

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Required for generation stage |
