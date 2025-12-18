import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from app.service import ChatManager
from app.models import ChatRequest, ChatResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import requests

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
:
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
#  ENTRY POINT
# ------------------------------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

