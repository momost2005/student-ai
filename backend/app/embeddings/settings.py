from sqlalchemy.orm import Session

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)


class EmbeddingSettings:

    PROVIDER_KEY = (
        "embedding.active_provider"
    )

    MODEL_KEY = (
        "embedding.active_model"
    )

    DIMENSIONS_KEY = (
        "embedding.dimensions"
    )


    def __init__(
        self,
        repository: SystemSettingsRepository
    ):

        self.repository = repository


    def get_active_provider(
        self,
        db: Session
    ) -> str:

        return (
            self.repository.get(
                db,
                self.PROVIDER_KEY
            )
            or "openai"
        )


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
    ) -> str:

        return (
            self.repository.get(
                db,
                self.MODEL_KEY
            )
            or "text-embedding-3-small"
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


    def get_dimensions(
        self,
        db: Session
    ) -> int | None:

        value = self.repository.get(
            db,
            self.DIMENSIONS_KEY
        )

        if not value:
            return None

        return int(value)


    def set_dimensions(
        self,
        db: Session,
        dimensions: int
    ) -> None:

        self.repository.set(
            db,
            self.DIMENSIONS_KEY,
            str(dimensions)
        )