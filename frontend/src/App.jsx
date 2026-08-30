import { useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [status, setStatus] = useState('Upload a PDF, then ask a grounded question.');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  async function uploadDocument() {
    if (!file) return setStatus('Choose a PDF first.');
    setLoading(true);
    const form = new FormData();
    form.append('file', file);
    try {
      const response = await fetch(`${API_URL}/documents`, { method: 'POST', body: form });
      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();
      setStatus(`Indexed ${data.chunks_indexed ?? 'document'} chunks successfully.`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function askQuestion(event) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setAnswer('');
    setSources([]);
    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      if (!response.ok) throw new Error('Question request failed');
      const data = await response.json();
      setAnswer(data.answer || 'No answer returned.');
      setSources(data.sources || []);
      setStatus('Answer generated from retrieved document context.');
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <span className="eyebrow">RAG · FastAPI · React · ChromaDB</span>
        <h1>Ask your documents.<br />Get grounded answers.</h1>
        <p>Upload a PDF, retrieve the most relevant chunks, and answer with visible source context.</p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>1. Index a document</h2>
          <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0])} />
          <button disabled={loading} onClick={uploadDocument}>Upload & index</button>
          <small>{status}</small>
        </article>

        <article className="card">
          <h2>2. Ask a question</h2>
          <form onSubmit={askQuestion}>
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="What are the main recommendations in this document?" />
            <button disabled={loading}>Ask document</button>
          </form>
        </article>
      </section>

      {answer && (
        <section className="result card">
          <h2>Answer</h2>
          <p>{answer}</p>
          <h3>Sources</h3>
          <div className="sources">
            {sources.length ? sources.map((source, index) => (
              <div className="source" key={index}>{typeof source === 'string' ? source : JSON.stringify(source)}</div>
            )) : <small>No source metadata returned.</small>}
          </div>
        </section>
      )}
    </main>
  );
}
