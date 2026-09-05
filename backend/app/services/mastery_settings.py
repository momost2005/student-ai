from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)


class MasterySettings:

    MINIMUM_UNIQUE_QUESTIONS_KEY = (
        "mastery.minimum_unique_questions"
    )

    MINIMUM_COVERAGE_PERCENT_KEY = (
        "mastery.minimum_coverage_percent"
    )

    PROFICIENT_THRESHOLD_KEY = (
        "mastery.proficient_threshold"
    )

    STRONG_THRESHOLD_KEY = (
        "mastery.strong_threshold"
    )


    def __init__(
        self,
        repository: SystemSettingsRepository
    ):

        self.repository = repository


    def get_minimum_unique_questions(
        self,
        db
    ) -> int:

        value = self.repository.get(
            db,
            self.MINIMUM_UNIQUE_QUESTIONS_KEY
        )

        if value is None:
            return 5

        return int(value)


    def get_minimum_coverage_percent(
        self,
        db
    ) -> float:

        value = self.repository.get(
            db,
            self.MINIMUM_COVERAGE_PERCENT_KEY
        )

        if value is None:
            return 10.0

        return float(value)


    def get_proficient_threshold(
        self,
        db
    ) -> float:

        value = self.repository.get(
            db,
            self.PROFICIENT_THRESHOLD_KEY
        )

        if value is None:
            return 75.0

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
            return 90.0

        return float(value)