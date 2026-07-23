import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "index"
INDEX_DIR.mkdir(exist_ok=True)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # runs locally, no API key needed

# "groq" or "huggingface" -- decides which client llm_providers.py builds
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")

if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
    raise RuntimeError("LLM_PROVIDER=groq but GROQ_API_KEY is not set")
if LLM_PROVIDER == "huggingface" and not HF_TOKEN:
    raise RuntimeError("LLM_PROVIDER=huggingface but HF_TOKEN is not set")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 4

FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
CHUNKS_STORE_PATH = INDEX_DIR / "chunks.json"


DEFAULT_FILES = {"SQL Notes by Apna College.pdf"}