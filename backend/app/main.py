# app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.rag_pipeline import RAGPipeline
from app.ingest import build_index
from app.config import DATA_DIR, INDEX_DIR, DEFAULT_FILES

ALLOWED_EXTENSIONS = (".txt", ".pdf", ".docx", ".md")

app = FastAPI(title="RAG Document Q&A System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rag-full-stack.vercel.app/"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

pipeline = None

@app.on_event("startup")
def load_pipeline():
    global pipeline
    if (INDEX_DIR / "index.faiss").exists():
        pipeline = RAGPipeline()
    else:
        pipeline = None

class QueryRequest(BaseModel):
    question: str

def current_files():
    return sorted(p.name for p in DATA_DIR.glob("*") if p.suffix.lower() in ALLOWED_EXTENSIONS)

@app.get("/files")
def list_files():
    return {"files": current_files()}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    dest = DATA_DIR / file.filename
    with open(dest, "wb") as f:
        f.write(await file.read())

    build_index()

    global pipeline
    pipeline = RAGPipeline()

    from app.chunking import load_and_chunk_directory
    records = load_and_chunk_directory(DATA_DIR)
    this_file_chunks = [r for r in records if r.metadata.get("source") == file.filename]

    if not this_file_chunks:
        return {
            "status": "warning",
            "filename": file.filename,
            "message": "File uploaded but no extractable text found, likely a scanned/image file",
            "files": current_files(),
        }

    return {"status": "indexed", "filename": file.filename, "chunks": len(this_file_chunks), "files": current_files()}

@app.delete("/files/{filename}")
def delete_file(filename: str):
    target = DATA_DIR / filename

    # Path-traversal guard: resolved path must still land inside DATA_DIR
    if target.resolve().parent != DATA_DIR.resolve():
        raise HTTPException(400, "Invalid filename")
    if not target.exists():
        raise HTTPException(404, "File not found")

    target.unlink()

    global pipeline
    remaining = current_files()

    # "no files left" cleanup branch
    if not remaining:
        for idx_file in (INDEX_DIR / "index.faiss", INDEX_DIR / "index.pkl"):
            if idx_file.exists():
                idx_file.unlink()
        pipeline = None
        return {"status": "deleted", "filename": filename, "files": []}

    build_index()
    pipeline = RAGPipeline()
    return {"status": "deleted", "filename": filename, "files": remaining}

@app.post("/query")
def query(request: QueryRequest):
    if pipeline is None:
        raise HTTPException(400, "No documents indexed yet. Upload a file first.")
    return pipeline.answer(request.question)

@app.post("/reset")
def reset_conversation():
    global pipeline

    if pipeline is None:
        raise HTTPException(400, "No documents indexed yet.")

    pipeline.reset_history()

    removed = []
    for file_path in DATA_DIR.glob("*"):
        if file_path.suffix.lower() in ALLOWED_EXTENSIONS and file_path.name not in DEFAULT_FILES:
            file_path.unlink()
            removed.append(file_path.name)

    remaining = current_files()

    if remaining:
        build_index()
        pipeline = RAGPipeline()
    else:
        for idx_file in (INDEX_DIR / "index.faiss", INDEX_DIR / "index.pkl"):
            if idx_file.exists():
                idx_file.unlink()
        pipeline = None

    return {"status": "reset", "removed": removed, "files": remaining}

@app.get("/health")
def health():
    return {"status": "ok", "index_loaded": pipeline is not None}