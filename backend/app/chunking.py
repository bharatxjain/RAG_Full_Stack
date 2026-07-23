# app/chunking.py
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def load_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        doc = Document(str(file_path))
        return "\n".join(p.text for p in doc.paragraphs)
    return file_path.read_text(encoding="utf-8", errors="ignore")   # .txt, .md

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = " ".join(text.split())
    chunks, start = [], 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def load_and_chunk_directory(data_dir: Path) -> list[dict]:
    records = []
    for file_path in sorted(data_dir.glob("*")):
        if file_path.suffix.lower() not in (".txt", ".pdf", ".docx", ".md"):
            continue
        text = load_text(file_path)
        for i, chunk in enumerate(chunk_text(text)):
            records.append({"text": chunk, "source": file_path.name, "chunk_id": f"{file_path.stem}_{i}"})
    return records