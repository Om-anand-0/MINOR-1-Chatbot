import os
import uuid
import json
import requests
from qdrant_client import QdrantClient
from app.embedder import Embedder

# ================= CONFIG =================
OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

MEDICAL_COLLECTION = "Medical_KB"
CHAT_MEMORY_COLLECTION = "chat_memory"

qdrant = QdrantClient(url=QDRANT_URL)

# ================= MEDICAL KB RETRIEVAL =================
def retrieve_medical_context(query: str, limit: int = 4) -> str:
    vector = Embedder.embed(query)
    if not vector:
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

# ================= CHAT MEMORY RETRIEVAL =================
def retrieve_chat_memory(query: str, limit: int = 2) -> str:
    vector = Embedder.embed(query)
    if not vector:
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

# ================= STORE CHAT MEMORY =================
def store_chat_memory(user_msg: str, bot_reply: str):
    summary = f"User: {user_msg}\nAssistant: {bot_reply}"

    vector = Embedder.embed(summary)
    if not vector:
        return

    qdrant.upsert(
        collection_name=CHAT_MEMORY_COLLECTION,
        points=[{
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {"text": summary}
        }]
    )

# ================= CHAT MANAGER =================
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

    # ---------- ADD USER MESSAGE ----------
    def add_user_message(self, message: str):
        self.chat.append({
            "role": "user",
            "content": message
        })

    # ---------- PAYLOAD BUILDER ----------
    def get_payload(self, messages, stream: bool):
        return {
            "model": self.model,
            "messages": messages,
            "temperature": 0.4,
            "num_predict": 150,
            "stream": stream
        }

    # ---------- BUILD PROMPT (SHARED) ----------
    def _build_prompt_messages(self):
        raw_user_msg = self.chat[-1]["content"]

        medical_ctx = retrieve_medical_context(raw_user_msg)
        memory_ctx = retrieve_chat_memory(raw_user_msg)

        prompt_messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        if medical_ctx:
            prompt_messages.append({
                "role": "system",
                "content": f"Relevant medical knowledge:\n{medical_ctx}"
            })

        if memory_ctx:
            prompt_messages.append({
                "role": "system",
                "content": f"Relevant past conversation:\n{memory_ctx}"
            })

        prompt_messages.extend(self.chat[-6:])
        return prompt_messages, raw_user_msg

    # ---------- NORMAL RESPONSE ----------
    def generate_response(self):
        prompt_messages, raw_user_msg = self._build_prompt_messages()

        payload = self.get_payload(prompt_messages, stream=False)
        response = requests.post(OLLAMA_CHAT_URL, json=payload).json()

        reply = response["message"]["content"]

        self.chat.append({
            "role": "assistant",
            "content": reply
        })

        store_chat_memory(raw_user_msg, reply)
        return reply

    # ---------- STREAMING RESPONSE ----------
    def generate_response_stream(self):
        prompt_messages, raw_user_msg = self._build_prompt_messages()
        payload = self.get_payload(prompt_messages, stream=True)

        full_reply = []

        with requests.post(OLLAMA_CHAT_URL, json=payload, stream=True) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line.decode("utf-8"))
                    token = data.get("message", {}).get("content")
                    if token:
                        full_reply.append(token)
                        yield token
                except Exception:
                    continue

        final_reply = "".join(full_reply)

        self.chat.append({
            "role": "assistant",
            "content": final_reply
        })

        store_chat_memory(raw_user_msg, final_reply)

    # ---------- RESET ----------
    def reset(self):
        self.__init__()

