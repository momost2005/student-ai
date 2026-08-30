from fastapi import FastAPI
from pydantic import BaseModel

from app.ai.gateway import AIGateway


app = FastAPI(
    title="Student AI API",
    version="0.1.0",
)

ai_gateway = AIGateway()


class AIRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "message": "Student AI backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/api/ai/chat")
def ai_chat(request: AIRequest):
    response = ai_gateway.generate(request.message)

    return {
        "response": response
    }