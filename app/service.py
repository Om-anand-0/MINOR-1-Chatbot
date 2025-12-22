import os
import requests
from qdrant_client import QdrantClient
from app.embedder import Embedder
import uuid
# ---------------- CONFIG ----------------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/chat")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

MEDICAL_COLLECTION = "Medical_KB"
CHAT_MEMORY_COLLECTION = "chat_memory"

qdrant = QdrantClient(url=QDRANT_URL)


# ---------------- MEDICAL KB RETRIEVAL ----------------
def retrieve_medical_context(query: str, limit: int = 4) -> str:
    vector = Embedder.embed(query)

    if not vector:
        print("⚠️ Skipping medical RAG: invalid embedding")
        return ""

    hits = qdrant.search(
        collection_name=MEDICAL_COLLECTION,
        query_vector=vector,
        limit=limit,
    )

    return "\n\n".join(
        hit.payload.get("text", "")[:400]
        for hit in hits
        if hit.payload.get("text")
    )


# ---------------- CHAT MEMORY RETRIEVAL ----------------
def retrieve_chat_memory(query: str, limit: int = 2) -> str:
    vector = Embedder.embed(query)

    if not vector:
        print("⚠️ Skipping memory search: invalid embedding")
        return ""

    hits = qdrant.search(
        collection_name=CHAT_MEMORY_COLLECTION,
        query_vector=vector,
        limit=limit,
    )

    return "\n".join(
        hit.payload.get("text", "")
        for hit in hits
        if hit.payload.get("text")
    )


# ---------------- STORE CHAT MEMORY ----------------
def store_chat_memory(user_msg: str, bot_reply: str):
    summary = f"User asked: {user_msg}\nAssistant replied: {bot_reply}"

    vector = Embedder.embed(summary)
    if not vector:
        print("⚠️ Skipping memory store: invalid embedding")
        return

    qdrant.upsert(
        collection_name=CHAT_MEMORY_COLLECTION,
        points=[{
            "id": str(uuid.uuid4()),   # ✅ FIX
            "vector": vector,
            "payload": {"text": summary}
        }]
    )


# ---------------- CHAT MANAGER ----------------
class ChatManager:
    def __init__(self):
        self.model = "phi3:mini"

        self.system_prompt = (
            "You are Swasth AI — a medical assistant. "
            "Provide safe, evidence-based medical information. "
            "Never provide emergency instructions or final diagnosis. "
            "Always recommend consulting a licensed doctor when appropriate."
        )

        self.chat = [
            {"role": "system", "content": self.system_prompt}
        ]

    def add_user_message(self, message: str):
        medical_ctx = retrieve_medical_context(message)
        memory_ctx = retrieve_chat_memory(message)

        enhanced_prompt = f"""
Medical knowledge (use if relevant):
{medical_ctx}

Previous conversation context:
{memory_ctx}

User question:
{message}
""".strip()

        self.chat.append({
            "role": "user",
            "content": enhanced_prompt
        })

    def get_payload(self, stream=False):
        if len(self.chat) > 12:
            self.chat = self.chat[:1] + self.chat[-10:]

        return {
            "model": self.model,
            "messages": self.chat,
            "temperature": 0.4,
            "num_predict": 150,
            "stream": stream
        }

    def generate_response(self):
        payload = self.get_payload(stream=False)

        response = requests.post(OLLAMA_HOST, json=payload).json()
        reply = response["message"]["content"]

        self.chat.append({"role": "assistant", "content": reply})

        # store memory
        user_msg = self.chat[-2]["content"]
        store_chat_memory(user_msg, reply)

        return reply

    def reset(self):
        self.__init__()

