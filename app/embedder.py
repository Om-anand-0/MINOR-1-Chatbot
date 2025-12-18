import requests

class Embedder:
    MODEL = "nomic-embed-text"
    URL = "http://localhost:11434/api/embeddings"

    @staticmethod
    def embed(text: str):
        try:
            payload = {
                "model": Embedder.MODEL,
                "prompt": text.strip()[:2000]  # safety
            }

            response = requests.post(Embedder.URL, json=payload)
            data = response.json()

            emb = data.get("embedding", [])
            if not emb:
                print("⚠️ Empty embedding returned!")
            return emb

        except Exception as e:
            print("❌ Embedding failed:", e)
            return []

