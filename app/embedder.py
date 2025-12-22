import requests
import os

class Embedder:
    MODEL = "nomic-embed-text"
    URL = os.getenv("OLLAMA_EMBED_URL", "http://localhost:11434/api/embed")

    @staticmethod
    def embed(text: str) -> list[float]:
        payload = {
            "model": Embedder.MODEL,
            "input": text.strip()[:2000],
        }

        try:
            r = requests.post(Embedder.URL, json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print("❌ Embedder HTTP error:", e)
            return []

        # Ollama returns a LIST of embeddings
        embeddings = data.get("embeddings")
        if not embeddings or not embeddings[0]:
            print("⚠️ Empty embedding from Ollama")
            return []

        emb = embeddings[0]

        if len(emb) != 768:
            print(f"⚠️ Wrong embedding dim: {len(emb)}")
            return []

        return emb

