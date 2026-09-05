from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)


class ConceptProgressSettings:

    MINIMUM_UNIQUE_ASSESSED_QUESTIONS_KEY = (
        "concept_progress."
        "minimum_unique_assessed_questions"
    )

    WEAK_THRESHOLD_KEY = (
        "concept_progress.weak_threshold"
    )

    STRONG_THRESHOLD_KEY = (
        "concept_progress.strong_threshold"
    )


    def __init__(
        self,
        repository: SystemSettingsRepository
    ):

        self.repository = repository


    def get_minimum_unique_assessed_questions(
        self,
        db
    ) -> int:

        value = self.repository.get(
            db,
            self.MINIMUM_UNIQUE_ASSESSED_QUESTIONS_KEY
        )

        if value is None:
            return 3

        return int(value)


    def get_weak_threshold(
        self,
        db
    ) -> float:

        value = self.repository.get(
            db,
            self.WEAK_THRESHOLD_KEY
        )

        if value is None:
            return 50.0

        return float(value)


    def get_strong_threshold(
        self,
        db
    ) -> float:

        value = self.repository.get(
            db,
            self.STRONG_THRESHOLD_KEY
        )

        if value is None:
            return 80.0

        return float(value)