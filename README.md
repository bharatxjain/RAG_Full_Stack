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
git clone https://github.com/bharatxjain/RAG_Full_Stack.git
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

Same as Option A, Step 2, `backend/.env` must exist with a real API key. Docker Compose reads this file directly, not your shell environment.

#### 3. Confirm your default demo document is present

```bash
ls backend/data
```
The app keeps a default document available even after a conversation reset (see `DEFAULT_FILES` in `backend/app/config.py`), make sure it's actually there before building.

#### 4. Build and start both containers

From the project root (not inside `backend/` or `frontend/`):
```bash
docker-compose up --build
```
First run takes a few minutes, it's downloading base images and installing dependencies fresh. Watch for `Application startup complete` in the backend logs before moving on.

Leave this terminal open, it shows live logs from both containers while they run.

#### 5. Verify both containers are actually up, in a separate terminal

```bash
docker ps
```
You should see exactly two rows: `rag-fullstack-backend-1` (port `0.0.0.0:8000->8000`) and `rag-fullstack-frontend-1` (port `0.0.0.0:3000->80`). If you see containers with different names, or none at all, something's wrong before you even open a browser, don't skip this check.

#### 6. Test the backend directly, before opening the app

```
http://localhost:8000/health
```
Should return `{"status": "ok", ...}`. Confirming this first isolates backend problems from frontend problems if something doesn't look right in Step 7.

#### 7. Open the app

```
http://localhost:3000
```

#### 8. Stop the containers

Back in the terminal running `docker-compose up`:
```
Ctrl + C
```
Or, to run in the background instead of watching logs:
```bash
docker-compose up -d
```
and to stop that later, from any terminal:
```bash
docker-compose down
```

#### If a rebuild after code changes doesn't pick up your latest changes

Docker aggressively caches layers, if something seems stale after editing code or `requirements.txt`, force a clean rebuild:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

#### Troubleshooting

| Symptom | Likely fix |
|---|---|
| `docker ps` shows a connection/pipe error | Docker Desktop isn't running, start it and wait before retrying |
| `localhost:3000` unreachable, but `docker ps` looks fine | Check the container names in `docker ps` output, if they don't match `rag-fullstack-backend-1`/`rag-fullstack-frontend-1`, you may have a leftover container from separate `docker run` testing occupying a different port; run `docker ps -a` to check for stray containers and remove unrelated ones |
| Backend build fails on `pip install` | Check `backend/requirements.txt` uses `>=` version ranges, not exact pins from a `pip freeze` on a different OS/Python version, exact Windows pins often don't resolve inside the Linux container |
| `/health` works but `/query` fails inside Docker only | `backend/.env` likely has placeholder values instead of your real API key, `env_file` reads it literally |

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
