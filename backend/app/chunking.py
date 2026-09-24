# app/chunking.py
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_SIZE, CHUNK_OVERLAP

class PlainTextLoader:
    """Replaces TextLoader: it defaults to the OS encoding (cp1252 on Windows) and its
    chardet fallback crashes on chardet>=6. Try UTF-8 first, then common Windows encodings."""
    ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")  # latin-1 decodes any byte, so this never fails

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        raw = Path(self.file_path).read_bytes()
        for encoding in self.ENCODINGS:
            try:
                return [Document(page_content=raw.decode(encoding), metadata={"source": self.file_path})]
            except UnicodeDecodeError:
                continue

LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": PlainTextLoader,
    ".md": PlainTextLoader,
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