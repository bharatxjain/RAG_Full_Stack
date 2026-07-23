# app/rag_pipeline.py
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from app.config import INDEX_DIR, EMBEDDING_MODEL_NAME, GROQ_API_KEY, GROQ_MODEL_NAME, TOP_K

class RAGPipeline:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = faiss.read_index(str(INDEX_DIR / "faiss.index"))
        with open(INDEX_DIR / "chunks.json") as f:
            self.chunks = json.load(f)
        self.client = Groq(api_key=GROQ_API_KEY)   # <- this line was missing/lost

    def retrieve(self, query, k=TOP_K):
        vec = self.embedder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(vec)
        _, indices = self.index.search(vec.astype(np.float32), k)
        return [self.chunks[i] for i in indices[0] if i != -1]

    def answer(self, query):
        retrieved = self.retrieve(query)
        context = "\n\n".join(f"[{r['source']}]\n{r['text']}" for r in retrieved)
        messages = [
            {"role": "system", "content": "Answer using only the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        response = self.client.chat.completions.create(model=GROQ_MODEL_NAME, messages=messages, temperature=0.2)
        return {
            "answer": response.choices[0].message.content,
            "sources": list({r["source"] for r in retrieved}),
        }