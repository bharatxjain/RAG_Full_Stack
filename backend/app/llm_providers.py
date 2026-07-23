"""
One function, get_llm_client(), returns an object with a single method:
generate(messages) -> str. Everything upstream (rag_pipeline.py) only
calls .generate(), it never knows or cares which provider is behind it.
"""
from groq import Groq
from huggingface_hub import InferenceClient

from app.config import (
    LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL_NAME, HF_TOKEN, HF_MODEL_NAME,
)


class GroqProvider:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL_NAME

    def generate(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=512,
        )
        return response.choices[0].message.content


class HuggingFaceProvider:
    def __init__(self):
        self.client = InferenceClient(model=HF_MODEL_NAME, token=HF_TOKEN)

    def generate(self, messages: list[dict]) -> str:
        response = self.client.chat_completion(messages=messages, max_tokens=512, temperature=0.2)
        return response.choices[0].message.content


def get_llm_client():
    if LLM_PROVIDER == "groq":
        return GroqProvider()
    if LLM_PROVIDER == "huggingface":
        return HuggingFaceProvider()
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")
