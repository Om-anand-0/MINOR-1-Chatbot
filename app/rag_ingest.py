import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from app.embedder import Embedder
from pypdf import PdfReader

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = "genzgpt_kb"

client = QdrantClient(url=QDRANT_URL)


# ----------------------------
#  FILE READERS
# ----------------------------

def read_pdf(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def read_md(path):
    return open(path, "r", encoding="utf-8").read()


def read_txt(path):
    return open(path, "r", encoding="utf-8").read()


def read_code(path):
    return open(path, "r", encoding="utf-8", errors="ignore").read()


# ----------------------------
#  TEXT CHUNKING
# ----------------------------

def chunk(text, max_len=400):
    words = text.split()
    chunks = []

    while len(words) > max_len:
        chunks.append(" ".join(words[:max_len]))
        words = words[max_len:]

    chunks.append(" ".join(words))
    return chunks


# ----------------------------
#  INGEST ENTIRE KB FOLDER
# ----------------------------

def ingest():
    kb_path = "kb"

    for root, _, files in os.walk(kb_path):
        for file in files:
            path = os.path.join(root, file)

            # detect file type
            if file.endswith(".pdf"):
                text = read_pdf(path)
            elif file.endswith(".md"):
                text = read_md(path)
            elif file.endswith(".txt"):
                text = read_txt(path)
            elif file.endswith((".py", ".js", ".cpp", ".java", ".ts", ".c", ".cs")):
                text = read_code(path)
            else:
                print(f"⚠️ Skipping unsupported file: {file}")
                continue

            # chunk + embed + upload
            for part in chunk(text):
                vec = Embedder.embed(part)
                if not vec:
                    continue

                client.upsert(
                    collection_name=COLLECTION,
                    points=[
                        PointStruct(
                            id=hash(part),
                            vector=vec,
                            payload={"text": part, "source": path}
                        )
                    ]
                )

    print("\n✅ Full ingestion completed successfully!")


# ----------------------------
#  INGEST SINGLE FILE
# ----------------------------

def ingest_file(path):
    if path.endswith(".pdf"):
        text = read_pdf(path)
    elif path.endswith(".md"):
        text = read_md(path)
    elif path.endswith(".txt"):
        text = read_txt(path)
    elif path.endswith((".py", ".js", ".cpp", ".java", ".ts", ".c", ".cs")):
        text = read_code(path)
    else:
        print(f"⚠️ Unsupported file: {path}")
        return

    for part in chunk(text):
        vec = Embedder.embed(part)
        if not vec:
            continue

        client.upsert(
            collection_name=COLLECTION,
            points=[
                PointStruct(
                    id=hash(part),
                    vector=vec,
                    payload={"text": part, "source": path}
                )
            ]
        )

    print(f"✅ Indexed file: {path}")


if __name__ == "__main__":
    ingest()

