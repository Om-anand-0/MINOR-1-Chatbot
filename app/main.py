import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from app.service import ChatManager
from app.models import ChatRequest, ChatResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import requests
import os
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
import shutil

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = ChatManager()


# ------------------------------
#  MODEL SWITCHING
# ------------------------------
@app.post("/set_model")
def set_model(model: str):
    bot.model = model
    return {"status": "ok", "model": model}


# ------------------------------
#  STREAMING CHAT ENDPOINT
# ------------------------------
@app.post("/chat/stream")
async def chat_stream(request: Request):

    body = await request.json()
    user_msg = body.get("message")

    bot.add_user_message(user_msg)

    # STREAM = TRUE
    payload = bot.get_payload(stream=True)

    ollama_url = bot.localHost

    def event_generator():
        with requests.post(ollama_url, json=payload, stream=True) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    decoded = json.loads(line.decode("utf-8"))
                    chunk = decoded.get("message", {}).get("content", "")
                    if chunk:
                        yield f"data: {chunk}\n\n"
                except:
                    continue

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ------------------------------
#  NORMAL NON-STREAM CHAT
# ------------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    bot.add_user_message(request.message)
    reply = bot.generate_response()
    return ChatResponse(reply=reply)


# ------------------------------
#  RESET MEMORY
# ------------------------------
@app.post("/reset")
def reset():
    bot.reset()
    return {"status": "chat memory cleared !"}

# ------------------------------
#  UPLOAD MEDICAL DOCUMENT (RAG)
# ------------------------------
@app.post("/upload")
def upload_medical_file(file: UploadFile = File(...)):

    ALLOWED_EXTENSIONS = (".pdf", ".txt")
    KB_DIR = "kb"

    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF or TXT files are supported"}
        )

    os.makedirs(KB_DIR, exist_ok=True)
    file_path = os.path.join(KB_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        from app.rag_ingest import ingest_file
        ingest_file(file_path)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Ingestion failed: {str(e)}"}
        )

    return {
        "status": "success",
        "filename": file.filename,
        "message": "Medical document indexed and ready for RAG"
    }

# ------------------------------
#  ENTRY POINT
# ------------------------------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

