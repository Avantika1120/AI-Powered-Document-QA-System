# AI-Powered Document Q&A System

A production-style document question-answering service built with **FastAPI, LangChain, embeddings, and ChromaDB**. The system ingests PDFs, splits them into searchable chunks, stores vector embeddings, retrieves the most relevant context, and returns answers with source citations.

## Why this project

Document-heavy teams often spend too much time searching through long PDFs, policies, reports, and knowledge bases. This project turns those documents into a searchable Q&A layer while preserving source traceability.

## Architecture

```text
PDF / text document
      |
      v
Document ingestion
      |
      v
Recursive text chunking
      |
      v
Sentence embeddings
      |
      v
Chroma vector store
      |
      v
Similarity retrieval
      |
      v
LLM context + answer generation
      |
      v
Answer + source citations
```

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service health check |
| `/documents` | POST | Upload and index a PDF |
| `/query` | POST | Ask a question over indexed documents |

## Tech stack

- Python
- FastAPI
- LangChain
- ChromaDB
- sentence-transformers
- OpenAI-compatible LLM integration
- PyPDF
- Docker
- Pytest
- GitHub Actions

## Local setup

```bash
git clone https://github.com/Avantika1120/AI-Powered-Document-QA-System.git
cd AI-Powered-Document-QA-System
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open Swagger UI at `http://localhost:8000/docs`.

## Example query

```json
POST /query
{
  "question": "What are the main risks discussed in the report?",
  "top_k": 4
}
```

Example response:

```json
{
  "answer": "...",
  "sources": [
    {"source": "annual_report.pdf", "page": 12}
  ]
}
```

## Engineering decisions

- **Source-grounded answers:** retrieved chunks retain document and page metadata.
- **Separation of concerns:** API routes are separated from retrieval logic.
- **Persistent vector storage:** Chroma persists embeddings between restarts.
- **Provider flexibility:** the service can use an OpenAI-compatible model when configured, while retrieval remains provider-independent.
- **Containerization:** Docker makes the service reproducible across environments.
- **CI:** GitHub Actions runs automated tests on every push and pull request.

## Project structure

```text
app/
  main.py
  rag.py
tests/
  test_api.py
.github/workflows/
  ci.yml
Dockerfile
requirements.txt
.env.example
```

## Resume alignment

This repository demonstrates the engineering behind a document Q&A application designed to support **large document collections, vector search, retrieval APIs, context construction, response validation, and source citation workflows**. Exact scale and answer-accuracy claims should be reproduced against the dataset/evaluation harness used for a specific deployment.

## Next improvements

- Add evaluation with groundedness and retrieval-recall metrics
- Add authentication and rate limiting
- Add S3 document ingestion
- Add async background indexing for large document batches
- Add Redis caching
- Deploy to AWS ECS/Lambda behind API Gateway
