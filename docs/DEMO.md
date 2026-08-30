# Demo walkthrough

## Start the backend

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Start the React client

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Demo flow

1. Choose a PDF from the upload card.
2. Click **Upload & index**. The backend loads the PDF, chunks it, embeds the chunks, and writes them to ChromaDB.
3. Enter a question that can be answered by the document.
4. Click **Ask document**.
5. The UI displays the generated/retrieval answer and source metadata returned by FastAPI.

## API-only demo

```bash
curl -F "file=@sample.pdf" http://localhost:8000/documents

curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the main recommendations?","top_k":4}'
```

The demo preview in `demo.svg` is an illustrative UI preview, not a benchmark screenshot. Model accuracy/scale claims should be reproduced with the corresponding evaluation dataset.
