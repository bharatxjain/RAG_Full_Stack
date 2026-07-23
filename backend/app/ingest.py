# app/ingest.py
"""Run with: python -m app.ingest, whenever data/ changes."""
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import DATA_DIR, INDEX_DIR, EMBEDDING_MODEL_NAME
from app.chunking import load_and_chunk_directory

def build_index():
    chunks = load_and_chunk_directory(DATA_DIR)
    if not chunks:
        raise RuntimeError(f"No documents found in {DATA_DIR}")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(INDEX_DIR))

    print(f"Indexed {len(chunks)} chunks")

if __name__ == "__main__":
    build_index()