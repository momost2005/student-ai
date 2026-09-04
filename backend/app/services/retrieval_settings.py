from sqlalchemy.orm import Session

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)


class RetrievalSettings:

    MINIMUM_SIMILARITY_KEY = (
        "retrieval.minimum_similarity"
    )


    def __init__(
        self,
        repository: SystemSettingsRepository
    ):

        self.repository = repository


    def get_minimum_similarity(
        self,
        db: Session
    ) -> float:

        value = self.repository.get(
            db,
            self.MINIMUM_SIMILARITY_KEY
        )

        if not value:
            return 0.55

        return float(value)


    def set_minimum_similarity(
        self,
        db: Session,
        value: float
    ) -> None:

        self.repository.set(
            db,
            self.MINIMUM_SIMILARITY_KEY,
            str(value)
        )