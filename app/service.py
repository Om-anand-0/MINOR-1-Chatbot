import requests
import os


class ChatManager:
    def __init__(self):
        self.model = "phi3:mini"
        self.localHost = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/chat")

        self.chat = [
            {
                "role": "system",
                "content": (
                    "You are Swasth AI — A medical assistant. "
                    "Provide medically safe, evidence-based guidance. "
                    "Never give emergency treatment or final diagnosis. "
                    "Recommend consulting a doctor for critical issues."
                )
            }
        ]

    def add_user_message(self, message):
        self.chat.append({"role": "user", "content": message})

    def get_payload(self, stream=False):
        if len(self.chat) > 12:
            self.chat = self.chat[:1] + self.chat[-10:]

        return {
            "model": self.model,
            "messages": self.chat,
            "temperature": 0.4,
            "num_predict": 150,
            "stream": stream,
        }

    def generate_response(self):
        payload = self.get_payload(stream=False)
        r = requests.post(self.localHost, json=payload).json()
        reply = r["message"]["content"]

        self.chat.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self.__init__()   # reset fully

