# app/ingest.py
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import DATA_DIR, INDEX_DIR, EMBEDDING_MODEL_NAME
from app.chunking import load_and_chunk_directory

# app/ingest.py
def build_index():
    records = load_and_chunk_directory(DATA_DIR)
    if not records:
        raise RuntimeError(f"No documents found in {DATA_DIR}")

    # Diagnostic: show chunk count per file
    from collections import Counter
    counts = Counter(r["source"] for r in records)
    for filename, count in counts.items():
        print(f"  {filename}: {count} chunks")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = [r["text"] for r in records]
    embeddings = model.encode(texts, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype(np.float32))

    faiss.write_index(index, str(INDEX_DIR / "faiss.index"))
    with open(INDEX_DIR / "chunks.json", "w") as f:
        json.dump(records, f)
    print(f"Indexed {len(records)} chunks from {len(counts)} files")
    
if __name__ == "__main__":
    build_index()