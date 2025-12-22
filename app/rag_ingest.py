import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from app.embedder import Embedder
from pypdf import PdfReader

# ---------------- CONFIG ----------------
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = "Medical_KB"

client = QdrantClient(url=QDRANT_URL)


# ----------------------------
#  FILE READERS
# ----------------------------

def read_pdf(path: str) -> str:
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def read_txt(path: str) -> str:
    return open(path, "r", encoding="utf-8").read()


# ----------------------------
#  TEXT CHUNKING
# ----------------------------

def chunk(text: str, max_len: int = 400):
    words = text.split()
    chunks = []

    while len(words) > max_len:
        chunks.append(" ".join(words[:max_len]))
        words = words[max_len:]

    if words:
        chunks.append(" ".join(words))

    return chunks


# ----------------------------
#  INGEST SINGLE FILE
# ----------------------------

def ingest_file(path: str):
    if path.endswith(".pdf"):
        text = read_pdf(path)
    elif path.endswith(".txt"):
        text = read_txt(path)
    else:
        print(f"⚠️ Unsupported file type: {path}")
        return

    for part in chunk(text):
        vec = Embedder.embed(part)

        if not vec or len(vec) != 768:
            print("⚠️ Skipping chunk: invalid embedding")
            continue

        client.upsert(
            collection_name=COLLECTION,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),   # ✅ SAFE ID
                    vector=vec,
                    payload={
                        "text": part,
                        "source": os.path.basename(path)
                    }
                )
            ]
        )

    print(f"✅ Indexed medical file: {path}")


# ----------------------------
#  INGEST ENTIRE KB FOLDER
# ----------------------------

def ingest_all():
    kb_path = "kb"

    for root, _, files in os.walk(kb_path):
        for file in files:
            path = os.path.join(root, file)
            ingest_file(path)

    print("✅ Full medical KB ingestion completed")


if __name__ == "__main__":
    ingest_all()

