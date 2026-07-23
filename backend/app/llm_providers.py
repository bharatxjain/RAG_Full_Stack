from langchain_groq import ChatGroq
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from app.config import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL_NAME, HF_TOKEN, HF_MODEL_NAME

def get_llm():
    """Returns a LangChain chat model, same interface regardless of provider."""
    if LLM_PROVIDER == "groq":
        return ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL_NAME, temperature=0.2)

    if LLM_PROVIDER == "huggingface":
        endpoint = HuggingFaceEndpoint(
            repo_id=HF_MODEL_NAME,
            huggingfacehub_api_token=HF_TOKEN,
            max_new_tokens=512,
            temperature=0.2,
        )
        return ChatHuggingFace(llm=endpoint)

    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")