# RAG Full-Stack: FastAPI + React + Docker

## Local development (no Docker, fastest for iterating)

**Backend:**
```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set LLM_PROVIDER=groq and GROQ_API_KEY=your_key
# (or LLM_PROVIDER=huggingface and HF_TOKEN=your_key)
python -m app.ingest        # builds the index from data/
uvicorn app.main:app --reload
```

**Frontend** (separate terminal):
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Running with Docker Compose (full containerized stack)

1. Set up `backend/.env` as above (real API keys, this file is never baked into the image).
2. Build the index once, locally, before containerizing (simplest for a portfolio project):
   ```
   cd backend && python -m app.ingest
   ```
   This writes `backend/index/faiss.index` and `chunks.json`, which docker-compose mounts into the container.
3. From the project root:
   ```
   docker-compose up --build
   ```
4. Open http://localhost:3000 (React, served by nginx)
   Backend API directly reachable at http://localhost:8000

## Why the index is a mounted volume, not baked into the image

Rebuilding the Docker image every time you add a document would be slow and
wasteful. Mounting `backend/index/` as a volume means you can re-run
`python -m app.ingest` and the running container picks up the new index
without a rebuild.

## Why VITE_API_URL is http://localhost:8000, not http://backend:8000

React code runs in the user's browser after the JS bundle is downloaded,
the browser has never heard of Docker's internal network or the "backend"
service name. Only server-to-server calls (which this project doesn't have
yet) could use that hostname. Anything the browser calls directly must use
an address the browser's machine can actually resolve.

## Switching between Groq and Hugging Face

Change one line in `backend/.env`:
```
LLM_PROVIDER=groq          # fast, needs GROQ_API_KEY
LLM_PROVIDER=huggingface   # needs HF_TOKEN
```
No code changes required, `llm_providers.py` handles the branching.

## What this demonstrates end to end

- **RAG**: chunking, embeddings, FAISS retrieval, prompt augmentation
- **FastAPI**: Pydantic validation, startup-time model loading, CORS
- **Provider abstraction**: swappable LLM backend, a real design pattern
- **React**: functional components, hooks (useState, useEffect, useRef), controlled forms
- **Docker**: multi-stage build for the frontend, layer-cached pip install for the backend
- **docker-compose**: multi-container orchestration, environment injection, volumes
