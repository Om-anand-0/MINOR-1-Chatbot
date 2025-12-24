import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from app.service import ChatManager
from app.models import ChatRequest, ChatResponse

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
#  STREAMING CHAT
# ------------------------------
@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_msg = body.get("message")

    bot.add_user_message(user_msg)

    def event_generator():
        for token in bot.generate_response_stream():
            yield f"data:{token}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# ------------------------------
#  NORMAL CHAT
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
    return {"status": "chat memory cleared"}

# ------------------------------
#  UPLOAD MEDICAL DOCUMENT
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
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from app.service import ChatManager
from app.models import ChatRequest, ChatResponse

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
#  STREAMING CHAT
# ------------------------------
@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_msg = body.get("message")

    bot.add_user_message(user_msg)

    def event_generator():
        for token in bot.generate_response_stream():
            yield f"data: {token}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# ------------------------------
#  NORMAL CHAT
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
    return {"status": "chat memory cleared"}

# ------------------------------
#  UPLOAD MEDICAL DOCUMENT
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
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

