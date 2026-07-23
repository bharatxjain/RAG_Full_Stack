## Getting Started

### Prerequisites

- **Python 3.11 or 3.12** (avoid 3.13/3.14 for now, some ML dependencies like `sentence-transformers` and `faiss-cpu` don't yet have stable wheels for the newest Python releases)
- **Node.js 18+** and npm
- **Docker Desktop** (only needed for the containerized run, not for local development)
- A **Groq API key** (free, get one at https://console.groq.com/keys) or a **Hugging Face token** (https://huggingface.co/settings/tokens)

---

### Option A: Run locally (recommended for development)

#### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/rag-fullstack.git
cd rag-fullstack
```

#### 2. Set up the backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

- **Windows (PowerShell):**

```powershell
  .\venv\Scripts\Activate.ps1
```

If you get an execution-policy error, run this once first:

```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- **macOS/Linux:**

```bash
  source venv/bin/activate
```

Confirm your prompt shows `(venv)` before continuing.

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up your environment variables:

```bash
cp .env.example .env
```

Open `.env` and add your real API key:

```
LLM_PROVIDER=groq
GROQ_API_KEY=your_actual_key_here
```

#### 3. Add documents and build the index

Drop any `.txt`, `.pdf`, or `.docx` files into `backend/data/`, then run:

```bash
python -m app.ingest
```

You should see something like `Indexed 62 chunks from 3 files`. Re-run this command any time you add or remove files directly in that folder (not needed if you use the in-app upload feature instead).

#### 4. Start the backend

```bash
uvicorn app.main:app --reload
```

If `uvicorn` isn't recognized on Windows, use:

```bash
python -m uvicorn app.main:app --reload
```

Confirm it's working by opening **http://127.0.0.1:8000/health**, you should see `{"status": "ok", ...}`. Leave this terminal running.

#### 5. Start the frontend (in a new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**.

You should now be able to upload a document, ask a question, and see a grounded answer with cited sources.

---

### Option B: Run with Docker Compose (containerized)

Use this once the local setup above works, Docker adds a layer of indirection that's harder to debug if the underlying code has a real bug.

#### 1. Make sure Docker Desktop is running

```bash
docker ps
```

This should return an empty table with headers, not a connection error. If it errors, open Docker Desktop from your Start menu/Applications and wait for it to fully start.

#### 2. Set up your `.env` file

Same as Option A, Step 2, `backend/.env` must exist with a real API key. Docker Compose reads this file directly.

#### 3. Build and start both containers

From the project root (not inside `backend/` or `frontend/`):

```bash
docker-compose up --build
```

First run takes a few minutes, it's downloading base images and installing dependencies fresh. Watch for `Application startup complete` in the backend logs.

#### 4. Open the app

**http://localhost:3000**

#### 5. Stop the containers

```bash
docker-compose down
```

Or, to run in the background instead of watching logs:

```bash
docker-compose up -d
```

---

### Switching between Groq and Hugging Face

Edit one line in `backend/.env`:

```
LLM_PROVIDER=groq          # requires GROQ_API_KEY
LLM_PROVIDER=huggingface   # requires HF_TOKEN
```

No code changes needed.

---

### Troubleshooting

| Symptom                                                                           | Likely fix                                                                                                             |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `uvicorn` not recognized                                                          | Virtual environment isn't activated, or use `python -m uvicorn ...` instead                                            |
| `ModuleNotFoundError: No module named 'fastapi'`                                  | `pip install -r requirements.txt` didn't complete, re-run it and watch for errors                                      |
| `Form data requires "python-multipart"`                                           | `pip install python-multipart`                                                                                         |
| `ERROR: Could not find a version that satisfies the requirement faiss-cpu==X.X.X` | Loosen the pin in `requirements.txt` to `faiss-cpu>=1.12.0`                                                            |
| Upload succeeds but answers ignore the new file                                   | Check the backend terminal for a chunk count of `0` for that file, likely a scanned/image PDF with no extractable text |
| Frontend shows an error but the backend logs show `200 OK`                        | Check `App.jsx` for a status-string mismatch (e.g. comparing against `"success"` when the backend returns `"indexed"`) |
| `docker-compose up` fails with a pipe/engine connection error                     | Docker Desktop isn't running, start it and wait for `docker ps` to succeed before retrying                             |
