# app/chunking.py
from pathlib import Path
from functools import partial
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_SIZE, CHUNK_OVERLAP

LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": partial(TextLoader, autodetect_encoding=True),
    ".md": partial(TextLoader, autodetect_encoding=True),
}

def load_and_chunk_directory(data_dir: Path):
    """Loads every supported file in data_dir and splits it into chunks.
    Returns LangChain Document objects, each already carrying source metadata."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    all_docs = []

    for file_path in sorted(data_dir.glob("*")):
        loader_cls = LOADERS.get(file_path.suffix.lower())
        if loader_cls is None:
            continue

        docs = loader_cls(str(file_path)).load()
        for doc in docs:
            doc.metadata["source"] = file_path.name

        all_docs.extend(docs)

    return splitter.split_documents(all_docs)