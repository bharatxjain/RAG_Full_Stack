# app/rag_pipeline.py
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

from app.config import INDEX_DIR, EMBEDDING_MODEL_NAME, TOP_K
from app.llm_providers import get_llm

MAX_HISTORY_TURNS = 6  # keep last 6 Q&A exchanges, bounds token usage per request

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a precise research assistant. Answer the question using ONLY the "
     "provided context. Be specific, quote exact figures or steps from the context "
     "where relevant. If the context doesn't contain the answer, say so directly, "
     "never guess. Use the conversation history to understand follow-up questions."),
    MessagesPlaceholder("history"),
    ("user", "Context:\n{context}\n\nQuestion: {question}"),
])

def format_docs(docs):
    return "\n\n".join(f"[{d.metadata.get('source', 'unknown')}]\n{d.page_content}" for d in docs)

class RAGPipeline:
    def __init__(self):
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.vectorstore = FAISS.load_local(str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": TOP_K})

        llm = get_llm()
        self.chain = prompt | llm | StrOutputParser()

        # In-memory only: resets on server restart, and is shared across every
        # browser tab/user since there's no per-session tracking yet. Fine for
        # a single-user portfolio demo, worth naming as a known limitation.
        self.history = []

    def answer(self, query: str) -> dict:
        retrieved_docs = self.retriever.invoke(query)   # note: retrieval itself doesn't use history yet
        context = format_docs(retrieved_docs)

        answer_text = self.chain.invoke({
            "context": context,
            "question": query,
            "history": self.history,
        })

        self.history.append(HumanMessage(content=query))
        self.history.append(AIMessage(content=answer_text))
        self.history = self.history[-(MAX_HISTORY_TURNS * 2):]   # trim, oldest exchanges drop off first

        return {
            "answer": answer_text,
            "sources": list({d.metadata.get("source", "unknown") for d in retrieved_docs}),
        }

    def reset_history(self):
        self.history = []