from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.ai.gateway import AIGateway
from app.ai.registry import AIProviderRegistry
from app.ai.settings import AISettings

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import get_db

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)

app = FastAPI(
    title="Student AI API",
    version="0.1.0",
)


# AI Infrastructure

ai_registry = AIProviderRegistry()
settings_repository = SystemSettingsRepository()

ai_settings = AISettings(
    repository=settings_repository
)

ai_gateway = AIGateway(
    registry=ai_registry,
    settings=ai_settings
)


# Request Models

class AIRequest(BaseModel):
    message: str


class AIProviderSettingRequest(BaseModel):
    provider: str

class AIModelSettingRequest(BaseModel):
    model: str
    
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
def ai_chat(
    request: AIRequest,
    db: Session = Depends(get_db)
):

    provider, model, response = (
        ai_gateway.generate(
            db=db,
            prompt=request.message
        )
    )

    return {
        "provider": provider,
        "model": model,
        "response": response
    }


@app.get("/api/ai/providers")
def get_ai_providers(
    db: Session = Depends(get_db)
):

    return {
        "active_provider":
            ai_settings.get_active_provider(db),

        "active_model":
            ai_settings.get_active_model(db),

        "providers":
            ai_registry.names()
    }


# Global Settings APIs

@app.put("/api/settings/ai/provider")
def set_ai_provider(
    request: AIProviderSettingRequest,
    db: Session = Depends(get_db)
):

    try:
        ai_registry.get(
            request.provider
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    ai_settings.set_active_provider(
        db,
        request.provider
    )

    return {
        "active_provider":
            ai_settings.get_active_provider(db)
    }

@app.put("/api/settings/ai/model")
def set_ai_model(
    request: AIModelSettingRequest,
    db: Session = Depends(get_db)
):

    ai_settings.set_active_model(
        db,
        request.model
    )

    return {
        "active_provider":
            ai_settings.get_active_provider(db),

        "active_model":
            ai_settings.get_active_model(db)
    }   

@app.get("/health/database")
def database_health(
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("SELECT current_database()")
    )

    database_name = result.scalar()

    return {
        "status": "ok",
        "database": database_name
    }
