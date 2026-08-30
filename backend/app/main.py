from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.ai.gateway import AIGateway
from app.ai.registry import AIProviderRegistry
from app.ai.settings import AISettings


app = FastAPI(
    title="Student AI API",
    version="0.1.0",
)


# AI Infrastructure

ai_registry = AIProviderRegistry()
ai_settings = AISettings()

ai_gateway = AIGateway(
    registry=ai_registry,
    settings=ai_settings
)


# Request Models

class AIRequest(BaseModel):
    message: str


class AIProviderSettingRequest(BaseModel):
    provider: str


# General APIs

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


# AI APIs

@app.post("/api/ai/chat")
def ai_chat(request: AIRequest):

    response = ai_gateway.generate(
        request.message
    )

    return {
        "provider": ai_settings.active_provider,
        "response": response
    }


@app.get("/api/ai/providers")
def get_ai_providers():

    return {
        "active_provider": ai_settings.active_provider,
        "providers": ai_registry.names()
    }


# Global Settings APIs

@app.put("/api/settings/ai/provider")
def set_ai_provider(
    request: AIProviderSettingRequest
):

    try:
        ai_registry.get(request.provider)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    ai_settings.set_active_provider(
        request.provider
    )

    return {
        "active_provider": ai_settings.active_provider
    }