from sqlalchemy.orm import Session

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)


class AISettings:

    PROVIDER_KEY = "ai.active_provider"
    MODEL_KEY = "ai.active_model"

    def __init__(
        self,
        repository: SystemSettingsRepository
    ):
        self.repository = repository


    def get_active_provider(
        self,
        db: Session
    ) -> str:

        value = self.repository.get(
            db,
            self.PROVIDER_KEY
        )

        return value or "mock"


    def set_active_provider(
        self,
        db: Session,
        provider_name: str
    ) -> None:

        self.repository.set(
            db,
            self.PROVIDER_KEY,
            provider_name
        )


    def get_active_model(
        self,
        db: Session
    ) -> str | None:

        return self.repository.get(
            db,
            self.MODEL_KEY
        )


    def set_active_model(
        self,
        db: Session,
        model_name: str
    ) -> None:

        self.repository.set(
            db,
            self.MODEL_KEY,
            model_name
        )