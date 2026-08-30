from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RAGService:
    """Owns document ingestion, vector retrieval, and answer generation."""

    def __init__(self, persist_directory: str = "data/chroma") -> None:
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
        )

    def ingest_pdf(self, file_path: str, display_name: str) -> int:
        pages = PyPDFLoader(file_path).load()
        chunks = self.splitter.split_documents(pages)
        for chunk in chunks:
            chunk.metadata["source"] = display_name
        self.vector_store.add_documents(chunks)
        return len(chunks)

    def retrieve(self, question: str, top_k: int = 4) -> list[Any]:
        return self.vector_store.similarity_search(question, k=top_k)

    def answer(self, question: str, top_k: int = 4) -> dict[str, Any]:
        docs = self.retrieve(question, top_k)
        if not docs:
            return {"answer": "No indexed context was found for this question.", "sources": []}

        context = "\n\n".join(doc.page_content for doc in docs)
        sources = []
        seen = set()
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page")
            key = (source, page)
            if key not in seen:
                sources.append({"source": source, "page": page + 1 if isinstance(page, int) else page})
                seen.add(key)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Retrieval still works without an LLM key. This makes local setup and CI predictable.
            return {
                "answer": "LLM generation is not configured. Relevant source passages were retrieved successfully.",
                "sources": sources,
                "context_preview": context[:1500],
            }

        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
        )
        prompt = (
            "Answer the question using only the supplied context. "
            "If the context is insufficient, say so. Keep the answer concise.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )
        response = llm.invoke(prompt)
        return {"answer": response.content, "sources": sources}
