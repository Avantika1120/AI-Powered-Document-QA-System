from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.rag import RAGService

load_dotenv()

app = FastAPI(
    title="AI-Powered Document Q&A",
    version="1.0.0",
    description="Upload PDFs, retrieve relevant context, and answer questions with source citations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGService(os.getenv("CHROMA_DIR", "data/chroma"))


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents")
def upload_document(file: UploadFile = File(...)) -> dict[str, int | str]:
    suffix = Path(file.filename or "document.pdf").suffix.lower()
    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    try:
        chunks = rag.ingest_pdf(temp_path, file.filename or "document.pdf")
    finally:
        Path(temp_path).unlink(missing_ok=True)

    return {"document": file.filename or "document.pdf", "chunks_indexed": chunks}


@app.post("/query")
def query_documents(payload: QueryRequest) -> dict:
    return rag.answer(payload.question, payload.top_k)
